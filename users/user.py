from flask import Blueprint, jsonify, request
from utils import get_connection


users_bp = Blueprint('users', __name__)

# -----------------------------------------------------------------------------
# GET /get-users
# Devuelve todos los usuarios registrados.
# Respuesta: Array de objetos usuario.
# -----------------------------------------------------------------------------
@users_bp.route('/get-users', methods=['GET'])
def get_users():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM user")
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        users = [dict(zip(column_names, row)) for row in rows]
        cur.close()
        conn.close()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# -----------------------------------------------------------------------------
# GET /get-user-by-email/<email>
# Devuelve la información de un usuario por su email y sincroniza sus ofertas.
# Respuesta:
#     200: Objeto usuario
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_bp.route('/get-user-by-email/<email>', methods=['GET'])
def get_user_by_email(email):
    try:
        conn = get_connection()
        cur = conn.cursor()
        # 1. Obtener el usuario por email
        cur.execute('SELECT * FROM "user" WHERE email = %s', (email,))
        row = cur.fetchone()
        print(f"Consulta por email: {email}, resultado: {row}")
        if row:
            column_names = [desc[0] for desc in cur.description]
            user = dict(zip(column_names, row))
            print(f"Usuario encontrado: {user}")
            id_user = user['id']
            # 2. Obtener todos los id_shop de current_shop
            cur.execute('SELECT id_shop FROM current_shop')
            current_shops = set(r[0] for r in cur.fetchall())
            # 3. Obtener todas las ofertas (id_shop) que tiene el usuario
            cur.execute('SELECT id_shop FROM user_shop WHERE id_user = %s', (id_user,))
            user_shops = set(r[0] for r in cur.fetchall())
            # 4. Añadir las ofertas de current_shop que el usuario no tenga
            to_add = current_shops - user_shops
            for id_shop in to_add:
                cur.execute(
                    "INSERT INTO user_shop (id_user, id_shop, time_to_spin) VALUES (%s, %s, NOW() - INTERVAL '24 hours')",
                    (id_user, id_shop)
                )
            # 5. Eliminar las ofertas que el usuario tenga y no estén en current_shop
            to_remove = user_shops - current_shops
            for id_shop in to_remove:
                cur.execute(
                    "DELETE FROM user_shop WHERE id_user = %s AND id_shop = %s",
                    (id_user, id_shop)
                )
            conn.commit()
        else:
            user = {"message": "Usuario no encontrado"}
            print(f"Usuario no encontrado para email: {email}")
        cur.close()
        conn.close()
        print(f"JSON devuelto: {user}")
        return jsonify(user)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# POST /add-user
# Añade un nuevo usuario y sus desbloqueos por defecto.
# Espera un JSON con los datos del usuario.
# Respuestas:
#     201: { "message": "Usuario y desbloqueos añadidos correctamente" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_bp.route('/add-user', methods=['POST'])
def add_user():
    try:
        data = request.json
        name = data['name']
        if len(name) > 12:
            name = name[:12]
        conn = get_connection()
        cur = conn.cursor()
        # Guardar la contraseña tal cual, sin hashear
        password = data.get('password', None)
        cur.execute("""
            INSERT INTO "user" (
                id, name, num_voren_money, num_aurum_money,
                icon_selected, banner_selected, email, skin_selected, password, anim_victory, anim_lose
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['id'],
            name,
            data.get('num_voren_money', 0),
            data.get('num_aurum_money', 0),
            data.get('icon_selected', 'NONE'),
            data.get('banner_selected', 'NONE'),
            data['email'],
            data.get('skin_selected', 'NONE'),
            password,
            data.get('anim_victory', 'NONE'),
            data.get('anim_lose', 'NONE')
        ))

        # Insertar los valores por defecto en la tabla "user_unlocks" para el nuevo usuario
        cur.execute("""
            INSERT INTO user_unlocks (
            user_id, icon_profile, banner_profile, skins_unlock, anim_victory, anim_lose
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['id'],
            ["NONE"],
            ["NONE"], 
            ["NONE"],
            ["NONE"],
            ["NONE"]
        ))

        # Insertar el usuario en user_competitive con valores 0
        cur.execute(
            'INSERT INTO user_competitive (id_user, trophies, max_meters_traveled) VALUES (%s, %s, %s)',
            (data['id'], 0, 0)
        )

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Usuario y desbloqueos añadidos correctamente"}), 201

    except Exception as e:
        # Registrar el error en los logs
        import traceback
        traceback.print_exc()
        # Devolver un mensaje de error más detallado
        return jsonify({"error": str(e)}), 500
    
# -----------------------------------------------------------------------------
# GET /get-user/<user_id>
# Devuelve la información de un usuario por su id.
# Respuesta:
#     200: Objeto usuario
#     404: { "error": "Usuario no encontrado" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_bp.route('/get-user/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM "user" WHERE id = %s', (user_id,))
        row = cur.fetchone()
        if row:
            column_names = [desc[0] for desc in cur.description]
            user = dict(zip(column_names, row))
        else:
            user = {"message": "Usuario no encontrado"}
        cur.close()
        conn.close()
        return jsonify(user)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# POST /update-icon-selected-by-id
# Actualiza el icono seleccionado de un usuario.
# Espera un JSON con 'id' y 'icon_selected'.
# Respuestas:
#     200: { "message": "icon_selected actualizado correctamente" }
#     400: { "error": "ID e icon_selected son requeridos" }
#     404: { "error": "Usuario no encontrado" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_bp.route('/update-icon-selected-by-id', methods=['POST'])
def update_icon_selected_by_id():
    try:
        data = request.json
        user_id = data.get('id')
        icon_selected = data.get('icon_selected')
        if not user_id or not icon_selected:
            return jsonify({"error": "ID e icon_selected son requeridos"}), 400

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('UPDATE "user" SET icon_selected = %s WHERE id = %s', (icon_selected, user_id))
        conn.commit()
        updated = cur.rowcount
        cur.close()
        conn.close()

        if updated:
            return jsonify({"message": "icon_selected actualizado correctamente"}), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# POST /update-banner-selected-by-id
# Actualiza el banner seleccionado de un usuario.
# Espera un JSON con 'id' y 'banner_selected'.
# Respuestas:
#     200: { "message": "banner_selected actualizado correctamente" }
#     400: { "error": "ID y banner_selected son requeridos" }
#     404: { "error": "Usuario no encontrado" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_bp.route('/update-banner-selected-by-id', methods=['POST'])
def update_banner_selected_by_id():
    try:
        data = request.json
        user_id = data.get('id')
        banner_selected = data.get('banner_selected')
        if not user_id or not banner_selected:
            return jsonify({"error": "ID y banner_selected son requeridos"}), 400

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('UPDATE "user" SET banner_selected = %s WHERE id = %s', (banner_selected, user_id))
        conn.commit()
        updated = cur.rowcount
        cur.close()
        conn.close()

        if updated:
            return jsonify({"message": "banner_selected actualizado correctamente"}), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# POST /update-skin-selected-by-id
# Actualiza el skin seleccionado de un usuario.
# Espera un JSON con 'id' y 'skin_selected'.
# Respuestas:
#     200: { "message": "skin_selected actualizado correctamente" }
#     400: { "error": "ID y skin_selected son requeridos" }
#     404: { "error": "Usuario no encontrado" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_bp.route('/update-skin-selected-by-id', methods=['POST'])
def update_skin_selected_by_id():
    try:
        data = request.json
        user_id = data.get('id')
        skin_selected = data.get('skin_selected')
        if not user_id or not skin_selected:
            return jsonify({"error": "ID y skin_selected son requeridos"}), 400

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('UPDATE "user" SET skin_selected = %s WHERE id = %s', (skin_selected, user_id))
        conn.commit()
        updated = cur.rowcount
        cur.close()
        conn.close()

        if updated:
            return jsonify({"message": "skin_selected actualizado correctamente"}), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# POST /update-aurum-money
# Actualiza la cantidad de aurum de un usuario.
# Espera un JSON con 'id' y 'num_aurum_money'.
# Respuestas:
#     200: { "message": "num_aurum_money actualizado correctamente" }
#     400: { "error": "ID y num_aurum_money son requeridos" }
#     404: { "error": "Usuario no encontrado" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_bp.route('/update-aurum-money', methods=['POST'])
def update_aurum_money():
    try:
        data = request.json
        user_id = data.get('id')
        num_aurum_money = data.get('num_aurum_money')
        if not user_id or num_aurum_money is None:
            return jsonify({"error": "ID y num_aurum_money son requeridos"}), 400

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('UPDATE "user" SET num_aurum_money = %s WHERE id = %s', (num_aurum_money, user_id))
        conn.commit()
        updated = cur.rowcount
        cur.close()
        conn.close()

        if updated:
            return jsonify({"message": "num_aurum_money actualizado correctamente"}), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# POST /update-voren-money
# Actualiza la cantidad de voren de un usuario.
# Espera un JSON con 'id' y 'num_voren_money'.
# Respuestas:
#     200: { "message": "num_voren_money actualizado correctamente" }
#     400: { "error": "ID y num_voren_money son requeridos" }
#     404: { "error": "Usuario no encontrado" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_bp.route('/update-voren-money', methods=['POST'])
def update_voren_money():
    try:
        data = request.json
        user_id = data.get('id')
        num_voren_money = data.get('num_voren_money')
        if not user_id or num_voren_money is None:
            return jsonify({"error": "ID y num_voren_money son requeridos"}), 400

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('UPDATE "user" SET num_voren_money = %s WHERE id = %s', (num_voren_money, user_id))
        conn.commit()
        updated = cur.rowcount
        cur.close()
        conn.close()

        if updated:
            return jsonify({"message": "num_voren_money actualizado correctamente"}), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# GET /get-aurum-by-id/<user_id>
# Devuelve la cantidad de aurum de un usuario por su id.
# Respuesta:
#     200: { "num_aurum_money": ... }
#     404: { "error": "Usuario no encontrado" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_bp.route('/get-aurum-by-id/<user_id>', methods=['GET'])
def get_aurum_by_id(user_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT num_aurum_money FROM "user" WHERE id = %s', (user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return jsonify({"num_aurum_money": row[0]})
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# GET /get-voren-by-id/<user_id>
# Devuelve la cantidad de voren de un usuario por su id.
# Respuesta:
#     200: { "num_voren_money": ... }
#     404: { "error": "Usuario no encontrado" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_bp.route('/get-voren-by-id/<user_id>', methods=['GET'])
def get_voren_by_id(user_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT num_voren_money FROM "user" WHERE id = %s', (user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return jsonify({"num_voren_money": row[0]})
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# POST /update-name-by-id
# Actualiza el nombre de un usuario.
# Espera un JSON con 'id' y 'name'.
# Respuestas:
#     200: { "message": "Nombre actualizado correctamente" }
#     400: { "error": "ID y name son requeridos" }
#     404: { "error": "Usuario no encontrado" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@users_bp.route('/update-name-by-id', methods=['POST'])
def update_name_by_id():
    try:
        data = request.json
        user_id = data.get('id')
        new_name = data.get('name')
        if not user_id or not new_name:
            return jsonify({"error": "ID y name son requeridos"}), 400

        if len(new_name) > 12:
            new_name = new_name[:12]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('UPDATE "user" SET name = %s WHERE id = %s', (new_name, user_id))
        conn.commit()
        updated = cur.rowcount
        cur.close()
        conn.close()

        if updated:
            return jsonify({"message": "Nombre actualizado correctamente"}), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500