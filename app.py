# ------------------- CONFIGURACIÓN E IMPORTS -------------------
from flask import Flask, request, jsonify
import psycopg2
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
# Importación de Blueprints: cada blueprint agrupa las rutas (endpoints) de un módulo funcional de la API.
# Esto permite organizar el código y separar la lógica de usuarios, tienda, pagos, emails, etc.
from users.user import users_bp 
from users_unlocks.user_unlocks import users_unlocks_bp
from shop.shop import shop_bp
from paypal.paypal import paypal_bp
from emailSend.email import email_bp
from user_shop.user_shop import userShop_bp
from current_shop.current_shop import current_shop_bp
from user_competitive.user_competitive import user_competitive_bp
from multiplayer.multiplayer import multiplayer_bp

# ------------------- UTILIDADES -------------------
# Función para obtener una conexión a la base de datos PostgreSQL usando variables de entorno.
# Centraliza la configuración de conexión y facilita el acceso seguro a la base de datos desde cualquier parte del proyecto.
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode=os.getenv("DB_SSLMODE")
    )

# ------------------- INICIALIZACIÓN FLASK -------------------
# Se crea la instancia principal de la aplicación Flask.
app = Flask(__name__)
# Configurar CORS para permitir todos los orígenes (puedes restringir si lo deseas)
CORS(app)
# Configurar rate limiting global (100 requests por minuto por IP)
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per minute"])
# Se registran todos los Blueprints en la app principal.
# Cada blueprint añade sus rutas/endpoints al servidor Flask, permitiendo modularidad y separación de lógica.
app.register_blueprint(users_bp)                # Rutas de gestión de usuarios
app.register_blueprint(users_unlocks_bp)        # Rutas de desbloqueos de usuario
app.register_blueprint(shop_bp)                 # Rutas de la tienda
app.register_blueprint(paypal_bp)               # Rutas de pagos y PayPal
app.register_blueprint(email_bp)                # Rutas de envío de emails
app.register_blueprint(userShop_bp)             # Rutas de relación usuario-tienda
app.register_blueprint(current_shop_bp)         # Rutas de la tienda actual
app.register_blueprint(user_competitive_bp)     # Rutas de modo competitivo
app.register_blueprint(multiplayer_bp)          # Rutas de modo multijugador

# ------------------- MIDDLEWARE DE SEGURIDAD -------------------
@app.before_request
def security_middleware():
    # Log detallado de la petición
    print(f"[SECURITY] {request.method} {request.path} from {request.remote_addr} | User-Agent: {request.headers.get('User-Agent')}")
    # Ejemplo de protección extra: rechazar peticiones con User-Agent vacío (bots)
    if not request.headers.get('User-Agent'):
        return jsonify({"error": "User-Agent requerido"}), 400


# ------------------- RUTAS GENERALES -------------------
# -----------------------------------------------------------------------------
# GET /
# Endpoint de prueba para comprobar que la API está conectada.
# Respuesta: Texto plano de bienvenida.
# -----------------------------------------------------------------------------
@app.route('/')
def home():
    return "AstroLeapApi conectada a NeonDB 🚀"
 
# -----------------------------------------------------------------------------
# GET /check-user-email/<email>
# Comprueba si existe un usuario con el email proporcionado.
# Respuesta:
#     200: { "exists": true/false }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@app.route('/check-user-email/<email>', methods=['GET'])
def check_user_email(email):
    try:
        conn = get_connection()
        cur = conn.cursor() 
        cur.execute('SELECT EXISTS (SELECT 1 FROM "user" WHERE email = %s)', (email,))
        exists = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({"exists": exists})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
# -----------------------------------------------------------------------------
# POST /update-password
# Actualiza la contraseña de un usuario dado su email.
# Espera un JSON con 'email' y 'new_password'.
# Respuestas:
#     200: { "message": "Contraseña actualizada correctamente" }
#     400: { "error": "Email y nueva contraseña son requeridos" }
#     404: { "error": "Usuario no encontrado" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@app.route('/update-password', methods=['POST'])
def update_password():
    try:
        data = request.json
        email = data.get('email')
        new_password = data.get('new_password')

        if not email or not new_password:
            return jsonify({"error": "Email y nueva contraseña son requeridos"}), 400

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT password FROM "user" WHERE email = %s', (email,))
        row = cur.fetchone()

        if row and row[0] == 'NONE':
            cur.close()
            conn.close()
            return jsonify({"error": "No se puede cambiar la contraseña porque es 'NONE'"}), 400

        # Guardar la nueva contraseña tal cual, sin hashear
        cur.execute('UPDATE "user" SET password = %s WHERE email = %s', (new_password, email))
        conn.commit()
        updated = cur.rowcount

        cur.close()
        conn.close()

        if updated:
            return jsonify({"message": "Contraseña actualizada correctamente"}), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        import traceback
        print("[SECURITY] Error interno ocultado")
        return jsonify({"error": "Error interno del servidor"}), 500

# -----------------------------------------------------------------------------
# POST /verify-password
# Verifica si la contraseña proporcionada es correcta para el email dado.
# Espera un JSON con 'email' y 'password'.
# Respuestas:
#     200: { "authenticated": true/false }
#     400: { "error": "Email y contraseña son requeridos" }
#     500: { "error": <mensaje de error> }
# -----------------------------------------------------------------------------
@app.route('/verify-password', methods=['POST'])
def verify_password():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email y contraseña son requeridos"}), 400

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT password FROM "user" WHERE email = %s', (email,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            stored_password = row[0]
            # Si el usuario es de Google (password == 'NONE'), nunca autentica
            if stored_password == 'NONE':
                return jsonify({"authenticated": False})
            # Comparar directamente la contraseña en texto plano
            if password == stored_password:
                return jsonify({"authenticated": True})
            else:
                return jsonify({"authenticated": False})
        else:
            return jsonify({"authenticated": False})
    except Exception as e:
        import traceback
        print("[SECURITY] Error interno ocultado")
        return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    app.run(debug=True)
