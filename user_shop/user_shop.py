from flask import Blueprint, jsonify, request
from utils import get_connection

userShop_bp = Blueprint('user_shop', __name__)

# Obtener todas las ofertas de un usuario
# -----------------------------------------------------------------------------
# GET /user_shop/<id_user>
# Devuelve todos los id_shop asociados a un usuario.
# Respuesta: Array de id_shop.
# -----------------------------------------------------------------------------
@userShop_bp.route('/user_shop/<id_user>', methods=['GET'])
def get_user_shops(id_user):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_shop FROM user_shop WHERE id_user = %s", (id_user,))
    rows = cursor.fetchall()
    conn.close()
    # Devuelve solo el array de id_shop
    return jsonify([row[0] for row in rows])

# -----------------------------------------------------------------------------
# PUT /user_shop_time_to_spin
# Modifica el campo time_to_spin de una relación user_shop.
# Espera un JSON con 'id_user', 'id_shop' y 'time_to_spin'.
# Respuestas:
#     200: { "message": "Updated" }
#     400: { "error": "Missing fields" }
# -----------------------------------------------------------------------------
@userShop_bp.route('/user_shop_time_to_spin', methods=['PUT'])
def update_time_to_spin():
    data = request.json
    id_user = str(data.get('id_user'))
    id_shop = str(data.get('id_shop'))
    time_to_spin = data.get('time_to_spin')
    if not (id_user and id_shop and time_to_spin):
        return jsonify({"error": "Missing fields"}), 400
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE user_shop SET time_to_spin = %s WHERE id_user = %s AND id_shop = %s",
        (time_to_spin, id_user, id_shop)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Updated"}), 200

# -----------------------------------------------------------------------------
# POST /user_shop_time_to_spin
# Crea una nueva relación user_shop.
# Espera un JSON con 'id_user', 'id_shop' y 'time_to_spin'.
# Respuestas:
#     201: { "message": "Created" }
#     400: { "error": "Missing fields" }
# -----------------------------------------------------------------------------
@userShop_bp.route('/user_shop_time_to_spin', methods=['POST'])
def create_user_shop():
    data = request.json
    id_user = data.get('id_user')
    id_shop = data.get('id_shop')
    time_to_spin = data.get('time_to_spin')
    if not (id_user and id_shop and time_to_spin):
        return jsonify({"error": "Missing fields"}), 400
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_shop (id_user, id_shop, time_to_spin) VALUES (%s, %s, %s)",
        (id_user, id_shop, time_to_spin)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Created"}), 201

# -----------------------------------------------------------------------------
# DELETE /user_shop_time_to_spin
# Elimina una relación user_shop.
# Espera un JSON con 'id_user' y 'id_shop'.
# Respuestas:
#     200: { "message": "Deleted" }
#     400: { "error": "Missing fields" }
# -----------------------------------------------------------------------------
@userShop_bp.route('/user_shop_time_to_spin', methods=['DELETE'])
def delete_user_shop():
    data = request.json
    id_user = data.get('id_user')
    id_shop = data.get('id_shop')
    if not (id_user and id_shop):
        return jsonify({"error": "Missing fields"}), 400
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM user_shop WHERE id_user = %s AND id_shop = %s",
        (id_user, id_shop)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"}), 200

# -----------------------------------------------------------------------------
# GET /user_shop_time_to_spin
# Lista todos los elementos de user_shop.
# Respuesta: Array de objetos con 'id_user', 'id_shop' y 'time_to_spin'.
# -----------------------------------------------------------------------------
@userShop_bp.route('/user_shop_time_to_spin', methods=['GET'])
def list_user_shops():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_user, id_shop, time_to_spin FROM user_shop")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([
        {"id_user": row[0], "id_shop": row[1], "time_to_spin": row[2]} for row in rows
    ])
