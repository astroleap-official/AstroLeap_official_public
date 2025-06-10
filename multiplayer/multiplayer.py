from flask import Blueprint, jsonify, request
from utils import get_connection

# Blueprint para agrupar las rutas relacionadas con el modo multijugador
multiplayer_bp = Blueprint('multiplayer', __name__)

# -----------------------------------------------------------------------------
# GET /rooms/first-available
# Busca y devuelve el código de la primera sala disponible (sin player2 asignado).
# Respuesta:
#     { 'room_code': <str> } o { 'room_code': None }
# -----------------------------------------------------------------------------
@multiplayer_bp.route('/rooms/first-available', methods=['GET'])
def get_first_available_room():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT room_code FROM multiplayer_rooms WHERE player2_id IS NULL LIMIT 1')
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify({'room_code': row[0]})
    else:
        return jsonify({'room_code': None})

# -----------------------------------------------------------------------------
# POST /rooms
# Crea una nueva sala multijugador con un player1 y un room_code.
# Si el player1 ya tenía una sala completa, la elimina antes de crear la nueva.
# Espera un JSON con 'room_code' y 'player1_id'.
# Respuestas:
#     201: { 'message': 'Room created' }
#     400: { 'error': 'room_code and player1_id required' } o error de base de datos
# -----------------------------------------------------------------------------
@multiplayer_bp.route('/rooms', methods=['POST'])
def create_room_player1():
    data = request.get_json()
    print('POST /rooms - JSON recibido:', data)
    room_code = data.get('room_code') if data else None
    player1_id = data.get('player1_id') if data else None
    print('room_code:', room_code)
    print('player1_id:', player1_id)
    if not room_code or not player1_id:
        print('Faltan campos obligatorios')
        return jsonify({'error': 'room_code and player1_id required'}), 400
    conn = get_connection()
    cur = conn.cursor()
    # Elimina salas completas previas de este jugador
    cur.execute('DELETE FROM multiplayer_rooms WHERE player1_id = %s AND player2_id IS NOT NULL', (player1_id,))
    print(f"Salas completas eliminadas para player1_id: {player1_id}")
    try:
        # Inserta la nueva sala
        cur.execute('INSERT INTO multiplayer_rooms (room_code, player1_id, player2_id) VALUES (%s, %s, %s)', (room_code, player1_id, None))
        conn.commit()
        print('Room creada correctamente')
        return jsonify({'message': 'Room created'}), 201
    except Exception as e:
        print('Error al crear room:', str(e))
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

# -----------------------------------------------------------------------------
# PUT /rooms/<room_code>/add-player2
# Añade un segundo jugador (player2) a una sala existente.
# Espera un JSON con 'player2_id'.
# Respuestas:
#     200: { 'message': 'player2_id updated' }
#     400: { 'error': 'player2_id required' }
#     404: { 'error': 'Room not found' }
# -----------------------------------------------------------------------------
@multiplayer_bp.route('/rooms/<room_code>/add-player2', methods=['PUT'])
def add_player2_to_room(room_code):
    data = request.get_json()
    player2_id = data.get('player2_id')
    if not player2_id:
        return jsonify({'error': 'player2_id required'}), 400
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('UPDATE multiplayer_rooms SET player2_id = %s WHERE room_code = %s', (player2_id, room_code))
    conn.commit()
    if cur.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Room not found'}), 404
    conn.close()
    return jsonify({'message': 'player2_id updated'})

# -----------------------------------------------------------------------------
# DELETE /rooms/<room_code>
# Elimina una sala específica según su room_code.
# Respuestas:
#     200: { 'message': 'Room deleted' }
#     404: { 'error': 'Room not found' }
# -----------------------------------------------------------------------------
@multiplayer_bp.route('/rooms/<room_code>', methods=['DELETE'])
def delete_room(room_code):
    print(f"Intentando eliminar room con room_code: {room_code}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM multiplayer_rooms WHERE room_code = %s', (room_code,))
    conn.commit()
    print(f"Filas eliminadas: {cur.rowcount}")
    if cur.rowcount == 0:
        conn.close()
        print('Room no encontrada para eliminar')
        return jsonify({'error': 'Room not found'}), 404
    conn.close()
    print('Room eliminada correctamente')
    return jsonify({'message': 'Room deleted'})

# -----------------------------------------------------------------------------
# GET /rooms/<room_code>
# Devuelve la información de una sala específica (room_code, player1_id, player2_id).
# Respuestas:
#     200: { 'room_code': ..., 'player1_id': ..., 'player2_id': ... }
#     404: { 'error': 'Room not found' }
# -----------------------------------------------------------------------------
@multiplayer_bp.route('/rooms/<room_code>', methods=['GET'])
def get_room_info(room_code):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT room_code, player1_id, player2_id FROM multiplayer_rooms WHERE room_code = %s', (room_code,))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify({'room_code': row[0], 'player1_id': row[1], 'player2_id': row[2]})
    else:
        return jsonify({'error': 'Room not found'}), 404


