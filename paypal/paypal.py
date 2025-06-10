from flask import Blueprint, jsonify, render_template, request
from utils import get_connection
import requests
import base64
import os

# -----------------------------------------------------------------------------
# Blueprint de PayPal: agrupa todas las rutas relacionadas con pagos y callbacks de PayPal.
# El template_folder indica dónde buscar las plantillas HTML para las respuestas visuales.
# -----------------------------------------------------------------------------
paypal_bp = Blueprint('paypal', __name__, template_folder="templates")

# -----------------------------------------------------------------------------
# Función auxiliar para obtener un access token de PayPal usando client_id y client_secret.
# Se utiliza para autenticar las peticiones a la API de PayPal.
# -----------------------------------------------------------------------------
def get_paypal_access_token():
    auth = base64.b64encode(
        f"{os.getenv('PAYPAL_CLIENT_ID')}:{os.getenv('PAYPAL_CLIENT_SECRET')}"
        .encode()
    ).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    resp = requests.post(
        f"{os.getenv('PAYPAL_API_BASE')}/v1/oauth2/token",
        headers=headers,
        data=data
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

# -----------------------------------------------------------------------------
# POST /create-paypal-order
# Crea una nueva orden de pago en PayPal y la registra en la base de datos.
# Espera un JSON con 'amount', 'amountAurum' y 'email'.
# Respuestas:
#     200: Objeto con los datos de la orden creada
#     400: { 'error': 'Amount and email_client are required' }
#     500: { 'error': 'Failed to fetch PayPal token' }
# -----------------------------------------------------------------------------
@paypal_bp.route("/create-paypal-order", methods=["POST"])
def create_paypal_order():
    payload = request.get_json() or {}
    amount = payload.get("amount")
    amountAurum = payload.get("amountAurum")
    email_client = payload.get("email")
    if not amount or not email_client:
        return jsonify({"error": "Amount and email_client are required"}), 400

    try:
        token = get_paypal_access_token()
    except Exception as e:
        return jsonify({"error": "Failed to fetch PayPal token", "details": str(e)}), 500

    url = f"{os.getenv('PAYPAL_API_BASE')}/v2/checkout/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    body = {
        "intent": "CAPTURE",
        "application_context": {
            "brand_name": "AstroLeap",
            "landing_page": "LOGIN",
            "user_action": "PAY_NOW",
            "return_url": os.getenv("PAYPAL_RETURN_URL"),   
            "cancel_url": os.getenv("PAYPAL_CANCEL_URL"), 
        },
        "purchase_units": [
            {
                "reference_id": "default",
                "amount": {
                    "currency_code": "USD",
                    "value": f"{float(amount):.2f}"
                }
            }
        ]
    }
    resp = requests.post(url, headers=headers, json=body)
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        return jsonify({
            "error": "PayPal order creation failed",
            "details": resp.json()
        }), resp.status_code

    order_data = resp.json()
    order_id = order_data.get("id")
    if order_id:
        conn = get_connection()
        cur = conn.cursor()
        # Eliminar órdenes de más de 48h para este usuario, excepto las que tienen state = 'done'
        cur.execute("""
            DELETE FROM orders 
            WHERE email_client = %s 
              AND state != 'done' 
              AND time_click_to_buy < NOW() - INTERVAL '48 hours'""", (email_client,))
        # Eliminar órdenes 'done' solo si tienen más de 2 semanas
        cur.execute("""
            DELETE FROM orders 
            WHERE email_client = %s 
              AND state = 'done' 
              AND time_click_to_buy < NOW() - INTERVAL '2 weeks'""", (email_client,))
        # Limitar a 4 órdenes activas (no 'done'): si hay 4, eliminar la más antigua
        cur.execute("SELECT order_id FROM orders WHERE email_client = %s AND state != 'done' ORDER BY time_click_to_buy ASC", (email_client,))
        active_orders = cur.fetchall()
        if len(active_orders) >= 4:
            oldest_order_id = active_orders[0][0]
            cur.execute('DELETE FROM orders WHERE order_id = %s', (oldest_order_id,))
        # Insertar la nueva orden con ammount
        cur.execute('INSERT INTO orders (order_id, email_client, time_click_to_buy, ammount) VALUES (%s, %s, NOW(), %s)', (order_id, email_client, amountAurum))
        conn.commit()
        # Obtener todos los order_id activos del usuario
        cur.execute('SELECT order_id FROM orders WHERE email_client = %s', (email_client,))
        all_active_orders = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()

    return jsonify(order_data), 200

# -----------------------------------------------------------------------------
# GET /check-paypal-order-status/<order_id>
# Consulta el estado de una orden de PayPal y la captura si está aprobada.
# Si la orden se completa, la elimina de la base de datos.
# Respuestas:
#     200: { 'completed': True/False, 'status': <estado> }
#     500: { 'error': <mensaje de error> }
# -----------------------------------------------------------------------------
@paypal_bp.route("/check-paypal-order-status/<order_id>", methods=["GET"])
def check_paypal_order_status(order_id):
    try:
        access_token = get_paypal_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(f"{os.getenv('PAYPAL_API_BASE')}/v2/checkout/orders/{order_id}", headers=headers)
        response.raise_for_status()

        order = response.json()
        status = order.get("status")

        # Solo capturar si está aprobado
        if status == "APPROVED":
            capture_result = capture_paypal_order(order_id, access_token)
            # Puedes revisar el resultado de la captura si quieres
            status = capture_result.get("status", status)

        if status == "COMPLETED":
            # Eliminar la orden de la base de datos si está completada
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute('DELETE FROM orders WHERE order_id = %s', (order_id,))
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                import traceback
                traceback.print_exc()
            return jsonify({"completed": True})
        else:
            return jsonify({"completed": False, "status": status})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# Función auxiliar para capturar una orden de PayPal (finalizar el pago).
# -----------------------------------------------------------------------------
def capture_paypal_order(order_id, access_token):
    url = f"{os.getenv('PAYPAL_API_BASE')}/v2/checkout/orders/{order_id}/capture"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    resp = requests.post(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

# -----------------------------------------------------------------------------
# GET /paypal-success
# Endpoint que muestra la página de éxito de compra de PayPal.
# Envía el email de confirmación de compra y marca la orden como 'done'.
# Respuesta: Renderiza la plantilla 'paypal_success.html'.
# -----------------------------------------------------------------------------
@paypal_bp.route("/paypal-success")
def paypal_success():
    token = request.args.get('token')
    payer_id = request.args.get('PayerID')

    if not token or not payer_id:
        return jsonify({"error": "Missing token or payer ID"}), 400

    # Recuperar el email_client y ammount de la tabla orders usando el token (order_id)
    email = None
    ammount = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT email_client, ammount FROM orders WHERE order_id = %s', (token,))
        row = cur.fetchone()
        if row:
            email = row[0]
            ammount = row[1]
            # Llamar a la función de email para enviar el correo de compra con el order_id y ammount
            try:
                from emailSend.email import send_email_purchase
                send_email_purchase(email, token, ammount)
            except Exception as e:
                import traceback
                traceback.print_exc()
        # Cambiar el campo state a 'done'
        cur.execute('UPDATE orders SET state = %s WHERE order_id = %s', ('done', token))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        import traceback
        traceback.print_exc()

    return render_template('paypal_success.html')

# -----------------------------------------------------------------------------
# GET /paypal-cancel
# Endpoint que muestra la página de cancelación de compra de PayPal.
# Si existe un token, elimina la orden asociada de la base de datos.
# Respuesta: Renderiza la plantilla 'paypal_cancel.html'.
# -----------------------------------------------------------------------------
@paypal_bp.route("/paypal-cancel")
def paypal_cancel():
    token = request.args.get('token')
    if token:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('DELETE FROM orders WHERE order_id = %s', (token,))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            import traceback
            traceback.print_exc()
    return render_template('paypal_cancel.html')

# -----------------------------------------------------------------------------
# GET /get-orders-by-email/<email_client>
# Devuelve todas las órdenes de compra asociadas a un email de cliente.
# Respuesta:
#     200: Array de objetos con los datos de cada orden
#     500: { 'error': <mensaje de error> }
# -----------------------------------------------------------------------------
@paypal_bp.route('/get-orders-by-email/<email_client>', methods=['GET'])
def get_orders_by_email(email_client):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM orders WHERE email_client = %s ORDER BY time_click_to_buy DESC', (email_client,))
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        orders = [dict(zip(column_names, row)) for row in rows]
        cur.close()
        conn.close()
        return jsonify(orders)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500