from flask import Blueprint, jsonify, request
from utils import get_connection


user_competitive_bp = Blueprint('user_competitive', __name__)

# -----------------------------------------------------------------------------
# GET /user_competitive/<id_user>
# Devuelve los datos competitivos de un usuario.
# Respuesta:
#     200: { 'id_user': ..., 'trophies': ..., 'max_meters_traveled': ... }
#     404: { 'error': 'Usuario no encontrado' }
# -----------------------------------------------------------------------------
@user_competitive_bp.route('/user_competitive/<id_user>', methods=['GET'])
def get_user_competitive(id_user):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM user_competitive WHERE id_user = %s', (id_user,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return jsonify({
            'id_user': row[0],
            'trophies': row[1],
            'max_meters_traveled': row[2]
        })
    else:
        return jsonify({'error': 'Usuario no encontrado'}), 404

# -----------------------------------------------------------------------------
# POST /user_competitive
# Crea un registro competitivo para un usuario.
# Espera un JSON con 'id_user', 'trophies' y 'max_meters_traveled'.
# Respuestas:
#     201: { 'message': 'Registro creado' }
#     400/500: { 'error': <mensaje de error> }
# -----------------------------------------------------------------------------
@user_competitive_bp.route('/user_competitive', methods=['POST'])
def create_user_competitive():
    data = request.json
    id_user = str(data.get('id_user'))
    trophies = data.get('trophies', 0)
    max_meters_traveled = data.get('max_meters_traveled', 0)
    if not id_user:
        return jsonify({'error': 'id_user es requerido'}), 400
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO user_competitive (id_user, trophies, max_meters_traveled) VALUES (%s, %s, %s)',
                    (id_user, trophies, max_meters_traveled))
        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': str(e)}), 500
    cur.close()
    conn.close()
    return jsonify({'message': 'Registro creado'}), 201

# -----------------------------------------------------------------------------
# PUT /user_competitive/<id_user>
# Actualiza los datos competitivos de un usuario.
# Espera un JSON con 'trophies' y/o 'max_meters_traveled'.
# Respuestas:
#     200: { 'message': 'Registro actualizado' }
#     400: { 'error': 'Nada que actualizar' }
# -----------------------------------------------------------------------------
@user_competitive_bp.route('/user_competitive/<id_user>', methods=['PUT'])
def update_user_competitive(id_user):
    data = request.json
    trophies = data.get('trophies')
    max_meters_traveled = data.get('max_meters_traveled')
    if trophies is None and max_meters_traveled is None:
        return jsonify({'error': 'Nada que actualizar'}), 400
    conn = get_connection()
    cur = conn.cursor()
    updates = []
    params = []
    if trophies is not None:
        updates.append('trophies = %s')
        params.append(trophies)
    if max_meters_traveled is not None:
        updates.append('max_meters_traveled = %s')
        params.append(max_meters_traveled)
    params.append(id_user)
    cur.execute(f'UPDATE user_competitive SET {", ".join(updates)} WHERE id_user = %s', tuple(params))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Registro actualizado'}), 200

# -----------------------------------------------------------------------------
# GET /user_competitive
# Lista todos los registros competitivos.
# Respuesta: Array de objetos con los datos competitivos de cada usuario.
# -----------------------------------------------------------------------------
@user_competitive_bp.route('/user_competitive', methods=['GET'])
def list_user_competitive():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM user_competitive')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([
        {'id_user': row[0], 'trophies': row[1], 'max_meters_traveled': row[2]} for row in rows
    ])

# -----------------------------------------------------------------------------
# GET /user_competitive/top-meters
# Devuelve el top 5 de usuarios con más metros recorridos.
# Respuesta: Array de objetos con los datos de los usuarios.
# -----------------------------------------------------------------------------
@user_competitive_bp.route('/user_competitive/top-meters', methods=['GET'])
def get_top_meters_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'SELECT id_user, trophies, max_meters_traveled FROM user_competitive ORDER BY max_meters_traveled DESC LIMIT 5'
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([
        {'id_user': row[0], 'trophies': row[1], 'max_meters_traveled': row[2]} for row in rows
    ])


# -----------------------------------------------------------------------------
# PUT /user_competitive/set-meters/<id_user>
# Cambia los metros recorridos de un usuario.
# Espera un JSON con 'max_meters_traveled'.
# Respuestas:
#     200: { 'message': 'Metros actualizados' }
#     400: { 'error': 'max_meters_traveled es requerido' }
# -----------------------------------------------------------------------------
@user_competitive_bp.route('/user_competitive/set-meters/<id_user>', methods=['PUT'])
def set_meters(id_user):
    data = request.json
    meters = data.get('max_meters_traveled')
    if meters is None:
        return jsonify({'error': 'max_meters_traveled es requerido'}), 400
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('UPDATE user_competitive SET max_meters_traveled = %s WHERE id_user = %s', (meters, id_user))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Metros actualizados'}), 200

# -----------------------------------------------------------------------------
# PUT /user_competitive/set-trophies/<id_user>
# Cambia las copas de un usuario.
# Espera un JSON con 'trophies'.
# Respuestas:
#     200: { 'message': 'Copas actualizadas' }
#     400: { 'error': 'trophies es requerido' }
# -----------------------------------------------------------------------------
@user_competitive_bp.route('/user_competitive/set-trophies/<id_user>', methods=['PUT'])
def set_trophies(id_user):
    data = request.json
    trophies = data.get('trophies')
    if trophies is None:
        return jsonify({'error': 'trophies es requerido'}), 400
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('UPDATE user_competitive SET trophies = %s WHERE id_user = %s', (trophies, id_user))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Copas actualizadas'}), 200

# -----------------------------------------------------------------------------
# GET /user_competitive/top-trophies
# Devuelve el top 5 de usuarios con más copas.
# Respuesta: Array de objetos con los datos de los usuarios.
# -----------------------------------------------------------------------------
@user_competitive_bp.route('/user_competitive/top-trophies', methods=['GET'])
def get_top_trophies_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'SELECT id_user, trophies, max_meters_traveled FROM user_competitive ORDER BY trophies DESC LIMIT 5'
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([
        {'id_user': row[0], 'trophies': row[1], 'max_meters_traveled': row[2]} for row in rows
    ])

# -----------------------------------------------------------------------------
# GET /user_competitive/top10-trophies
# Devuelve el top 10 de usuarios con más copas.
# Respuesta: Array de objetos con los datos de los usuarios.
# -----------------------------------------------------------------------------
@user_competitive_bp.route('/user_competitive/top10-trophies', methods=['GET'])
def get_top10_trophies_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'SELECT id_user, trophies, max_meters_traveled FROM user_competitive ORDER BY trophies DESC LIMIT 10'
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([
        {'id_user': row[0], 'trophies': row[1], 'max_meters_traveled': row[2]} for row in rows
    ])

# -----------------------------------------------------------------------------
# GET /user_competitive/top10-meters
# Devuelve el top 10 de usuarios con más metros recorridos.
# Respuesta: Array de objetos con los datos de los usuarios.
# -----------------------------------------------------------------------------
@user_competitive_bp.route('/user_competitive/top10-meters', methods=['GET'])
def get_top10_meters_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'SELECT id_user, trophies, max_meters_traveled FROM user_competitive ORDER BY max_meters_traveled DESC LIMIT 10'
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([
        {'id_user': row[0], 'trophies': row[1], 'max_meters_traveled': row[2]} for row in rows
    ])