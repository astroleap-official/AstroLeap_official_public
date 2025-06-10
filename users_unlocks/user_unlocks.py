from flask import Blueprint, jsonify, request
from utils import get_connection
import json


users_unlocks_bp = Blueprint('users_unlocks', __name__)

# -----------------------------------------------------------------------------
# GET /get-user-unlocks/<user_id>
# Devuelve los desbloqueos de un usuario.
# Respuesta:
#     200: Objeto con los desbloqueos o mensaje si no hay datos.
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_unlocks_bp.route('/get-user-unlocks/<user_id>', methods=['GET'])
def get_user_unlocks(user_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM user_unlocks WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        if row:
            column_names = [desc[0] for desc in cur.description]
            result = dict(zip(column_names, row))
        else:
            result = {"message": "No se encontraron desbloqueos para el usuario"}
        cur.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# POST /add-user-unlocks
# Añade desbloqueos a un usuario.
# Espera un JSON con los campos de desbloqueos.
# Respuestas:
#     201: { "message": "Desbloqueos añadidos correctamente" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_unlocks_bp.route('/add-user-unlocks', methods=['POST'])
def add_user_unlocks():
    try:
        data = request.json
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO user_unlocks (
                user_id, icon_profile, banner_profile, skins_unlock, anim_victory, anim_lose
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['user_id'],
            data.get('icon_profile', []),
            data.get('banner_profile', []),
            data.get('skins_unlock', []),
            data.get('anim_victory', []),
            data.get('anim_lose', [])
        ))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Desbloqueos añadidos correctamente"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# -----------------------------------------------------------------------------
# POST /update-anim-victory-by-id
# Actualiza la animación de victoria de un usuario.
# Espera un JSON con 'id' y 'anim_victory'.
# Respuestas:
#     200: { "message": "anim_victory actualizado correctamente" }
#     400: { "error": "ID y anim_victory son requeridos" }
#     404: { "error": "Usuario no encontrado" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_unlocks_bp.route('/update-anim-victory-by-id', methods=['POST'])
def update_anim_victory_by_id():
    try:
        data = request.json
        user_id = data.get('id')
        anim_victory = data.get('anim_victory')
        if not user_id or not anim_victory:
            return jsonify({"error": "ID y anim_victory son requeridos"}), 400

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('UPDATE "user" SET anim_victory = %s WHERE id = %s', (anim_victory, user_id))
        conn.commit()
        updated = cur.rowcount
        cur.close()
        conn.close()

        if updated:
            return jsonify({"message": "anim_victory actualizado correctamente"}), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# POST /update-anim-lose-by-id
# Actualiza la animación de derrota de un usuario.
# Espera un JSON con 'id' y 'anim_lose'.
# Respuestas:
#     200: { "message": "anim_lose actualizado correctamente" }
#     400: { "error": "ID y anim_lose son requeridos" }
#     404: { "error": "Usuario no encontrado" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_unlocks_bp.route('/update-anim-lose-by-id', methods=['POST'])
def update_anim_lose_by_id():
    try:
        data = request.json
        user_id = data.get('id')
        anim_lose = data.get('anim_lose')
        if not user_id or not anim_lose:
            return jsonify({"error": "ID y anim_lose son requeridos"}), 400

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('UPDATE "user" SET anim_lose = %s WHERE id = %s', (anim_lose, user_id))
        conn.commit()
        updated = cur.rowcount
        cur.close()
        conn.close()

        if updated:
            return jsonify({"message": "anim_lose actualizado correctamente"}), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
def python_list_to_pg_array(py_list):
    # Convierte una lista de Python a formato array de PostgreSQL
    return '{' + ','.join('"{}"'.format(str(x).replace('"', '\"')) for x in py_list) + '}'

# -----------------------------------------------------------------------------
# POST /add-icon-profile
# Añade un icono al perfil de un usuario.
# Espera un JSON con 'user_id' y 'icon_profile'.
# Respuestas:
#     200: { "message": "Icono añadido correctamente" }
#     400: { "error": "user_id y icon_profile son requeridos" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_unlocks_bp.route('/add-icon-profile', methods=['POST'])
def add_icon_profile():
    try:
        data = request.json
        user_id = data.get('user_id')
        new_icon = data.get('icon_profile')
        if not user_id or new_icon is None:
            return jsonify({"error": "user_id y icon_profile son requeridos"}), 400

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT icon_profile FROM user_unlocks WHERE user_id = %s', (user_id,))
        row = cur.fetchone()
        icons = row[0] if row and row[0] else []
        if isinstance(icons, str):
            # Convierte el string de PostgreSQL array a lista de Python
            icons = [x.strip('"') for x in icons.strip('{}').split(',')] if icons else []
        if new_icon not in icons:
            icons.append(new_icon)
            pg_array = python_list_to_pg_array(icons)
            cur.execute('UPDATE user_unlocks SET icon_profile = %s WHERE user_id = %s', (pg_array, user_id))
            conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Icono añadido correctamente"}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# POST /add-banner-profile
# Añade un banner al perfil de un usuario.
# Espera un JSON con 'user_id' y 'banner_profile'.
# Respuestas:
#     200: { "message": "Banner añadido correctamente" }
#     400: { "error": "user_id y banner_profile son requeridos" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_unlocks_bp.route('/add-banner-profile', methods=['POST'])
def add_banner_profile():
    try:
        data = request.json
        user_id = data.get('user_id')
        new_banner = data.get('banner_profile')
        if not user_id or new_banner is None:
            return jsonify({"error": "user_id y banner_profile son requeridos"}), 400

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT banner_profile FROM user_unlocks WHERE user_id = %s', (user_id,))
        row = cur.fetchone()
        banners = row[0] if row and row[0] else []
        if isinstance(banners, str):
            banners = [x.strip('"') for x in banners.strip('{}').split(',')] if banners else []
        if new_banner not in banners:
            banners.append(new_banner)
            pg_array = python_list_to_pg_array(banners)
            cur.execute('UPDATE user_unlocks SET banner_profile = %s WHERE user_id = %s', (pg_array, user_id))
            conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Banner añadido correctamente"}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# POST /add-skin-unlock
# Añade un skin desbloqueado a un usuario.
# Espera un JSON con 'user_id' y 'skin_unlock'.
# Respuestas:
#     200: { "message": "Skin añadido correctamente" }
#     400: { "error": "user_id y skin_unlock son requeridos" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_unlocks_bp.route('/add-skin-unlock', methods=['POST'])
def add_skin_unlock():
    try:
        data = request.json
        user_id = data.get('user_id')
        new_skin = data.get('skin_unlock')
        if not user_id or new_skin is None:
            return jsonify({"error": "user_id y skin_unlock son requeridos"}), 400

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT skins_unlock FROM user_unlocks WHERE user_id = %s', (user_id,))
        row = cur.fetchone()
        skins = row[0] if row and row[0] else []
        if isinstance(skins, str):
            skins = [x.strip('"') for x in skins.strip('{}').split(',')] if skins else []
        if new_skin not in skins:
            skins.append(new_skin)
            pg_array = python_list_to_pg_array(skins)
            cur.execute('UPDATE user_unlocks SET skins_unlock = %s WHERE user_id = %s', (pg_array, user_id))
            conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Skin añadido correctamente"}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# POST /add-anim-victory
# Añade una animación de victoria a un usuario.
# Espera un JSON con 'user_id' y 'anim_victory'.
# Respuestas:
#     200: { "message": "Animación de victoria añadida correctamente" }
#     400: { "error": "user_id y anim_victory son requeridos" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_unlocks_bp.route('/add-anim-victory', methods=['POST'])
def add_anim_victory():
    try:
        data = request.json
        user_id = data.get('user_id')
        new_anim = data.get('anim_victory')
        if not user_id or new_anim is None:
            return jsonify({"error": "user_id y anim_victory son requeridos"}), 400

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT anim_victory FROM user_unlocks WHERE user_id = %s', (user_id,))
        row = cur.fetchone()
        anims = row[0] if row and row[0] else []
        if isinstance(anims, str):
            anims = [x.strip('"') for x in anims.strip('{}').split(',')] if anims else []
        if new_anim not in anims:
            anims.append(new_anim)
            pg_array = python_list_to_pg_array(anims)
            cur.execute('UPDATE user_unlocks SET anim_victory = %s WHERE user_id = %s', (pg_array, user_id))
            conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Animación de victoria añadida correctamente"}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# POST /add-anim-lose
# Añade una animación de derrota a un usuario.
# Espera un JSON con 'user_id' y 'anim_lose'.
# Respuestas:
#     200: { "message": "Animación de derrota añadida correctamente" }
#     400: { "error": "user_id y anim_lose son requeridos" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_unlocks_bp.route('/add-anim-lose', methods=['POST'])
def add_anim_lose():
    try:
        data = request.json
        user_id = data.get('user_id')
        new_anim = data.get('anim_lose')
        if not user_id or new_anim is None:
            return jsonify({"error": "user_id y anim_lose son requeridos"}), 400

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT anim_lose FROM user_unlocks WHERE user_id = %s', (user_id,))
        row = cur.fetchone()
        anims = row[0] if row and row[0] else []
        if isinstance(anims, str):
            anims = [x.strip('"') for x in anims.strip('{}').split(',')] if anims else []
        if new_anim not in anims:
            anims.append(new_anim)
            pg_array = python_list_to_pg_array(anims)
            cur.execute('UPDATE user_unlocks SET anim_lose = %s WHERE user_id = %s', (pg_array, user_id))
            conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Animación de derrota añadida correctamente"}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500