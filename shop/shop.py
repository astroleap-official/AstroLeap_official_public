from flask import Blueprint, jsonify, request
from utils import get_connection


shop_bp = Blueprint('shop', __name__)

# -----------------------------------------------------------------------------
# GET /get-shop
# Devuelve todos los ítems de la tienda.
# Respuesta: Array de objetos con los datos de cada ítem.
# -----------------------------------------------------------------------------
@shop_bp.route('/get-shop', methods=['GET'])
def get_shop():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM shop")
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        shop_items = [dict(zip(column_names, row)) for row in rows]
        cur.close()
        conn.close()
        return jsonify(shop_items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# POST /add-shop-item
# Añade un nuevo ítem a la tienda.
# Espera un JSON con 'type_offer' y 'elements_offer'.
# Respuestas:
#     201: { "message": "Ítem de tienda añadido correctamente" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@shop_bp.route('/add-shop-item', methods=['POST'])
def add_shop_item():
    try:
        data = request.json
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO shop (
                type_offer, elements_offer
            ) VALUES (%s, %s)
        """, (
            data['type_offer'],
            data.get('elements_offer', [])
        ))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Ítem de tienda añadido correctamente"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# -----------------------------------------------------------------------------
# GET /get-shop-item/<item_id>
# Devuelve la información de un ítem de la tienda por su id.
# Respuesta:
#     200: Objeto con los datos del ítem
#     404: { "error": "Ítem no encontrado" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@shop_bp.route('/get-shop-item/<int:item_id>', methods=['GET'])
def get_shop_item(item_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM shop WHERE id = %s', (item_id,))
        row = cur.fetchone()
        if row:
            column_names = [desc[0] for desc in cur.description]
            item = dict(zip(column_names, row))
            result = jsonify(item)
        else:
            result = jsonify({"error": "Ítem no encontrado"}), 404
        cur.close()
        conn.close()
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500