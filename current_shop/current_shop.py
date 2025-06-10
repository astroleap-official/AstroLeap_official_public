from flask import Blueprint, jsonify, request
from utils import get_connection

current_shop_bp = Blueprint('current_shop', __name__)

# Obtener todos los id_shop actuales
# -----------------------------------------------------------------------------
# GET /current_shop
# Devuelve todos los id_shop actuales disponibles en la tienda.
# Respuesta: Array de id_shop.
# -----------------------------------------------------------------------------
@current_shop_bp.route('/current_shop', methods=['GET'])
def get_current_shops():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_shop FROM current_shop")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([row[0] for row in rows])

# -----------------------------------------------------------------------------
# POST /current_shop
# Añade un nuevo id_shop a la tienda actual.
# Espera un JSON con 'id_shop'.
# Respuestas:
#     201: { "message": "Current shop added", "id_shop": <id_shop> }
#     400: { "error": "Missing id_shop" }
# -----------------------------------------------------------------------------
@current_shop_bp.route('/current_shop', methods=['POST'])
def add_current_shop():
    data = request.json
    id_shop = data.get('id_shop')
    if not id_shop:
        return jsonify({"error": "Missing id_shop"}), 400
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO current_shop (id_shop) VALUES (?)", (id_shop,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Current shop added", "id_shop": id_shop}), 201