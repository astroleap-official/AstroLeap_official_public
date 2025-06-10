import os
from flask import Blueprint, jsonify, request
from utils import get_connection
from email.message import EmailMessage
import smtplib

email_bp = Blueprint('email', __name__)

# -----------------------------------------------------------------------------
# POST /send-verification-email
# Envía un correo de verificación a un usuario nuevo.
# Espera un JSON con 'email', 'username' y 'code'.
# Respuestas:
#     200: { 'message': 'Email de verificación enviado correctamente' }
#     500: { 'error': <mensaje de error> }
# -----------------------------------------------------------------------------
@email_bp.route('/send-verification-email', methods=['POST'])
def send_verification_email():
    try:
        data = request.json
        email = data['email']
        username = data['username']
        code = data['code']

        # Enviar el correo electrónico
        send_email_simple(email, username, code)

        return jsonify({"message": "Email de verificación enviado correctamente"}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
# -----------------------------------------------------------------------------
# POST /send-forgot-password
# Envía un correo con código de recuperación de contraseña.
# Espera un JSON con 'email', 'username' y 'code'.
# Respuestas:
#     200: { 'message': 'Email de verificación enviado correctamente' }
#     500: { 'error': <mensaje de error> }
# -----------------------------------------------------------------------------
@email_bp.route('/send-forgot-password', methods=['POST'])
def send_forgot_verofication_email():
    try:
        data = request.json
        email = data['email']
        username = data['username']
        code = data['code']

        # Enviar el correo electrónico
        send_forgot_email_code(email, username, code)

        return jsonify({"message": "Email de verificación enviado correctamente"}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# POST /send-email-buy-product
# Envía un correo de confirmación de compra a un usuario.
# Espera un JSON con 'email'.
# Respuestas:
#     200: { 'message': 'Email de verificación enviado correctamente' }
#     500: { 'error': <mensaje de error> }
# -----------------------------------------------------------------------------
@email_bp.route('/send-email-buy-product', methods=['POST'])
def send_buy_product_email():
    try:
        data = request.json
        email = data['email']
        send_email_purchase(email)

        return jsonify({"message": "Email de verificación enviado correctamente"}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
# -----------------------------------------------------------------------------
# MÉTODO AUXILIAR
# Envía un correo de confirmación de compra al usuario.
# Parámetros:
#   email (str): Email del destinatario.
#   order_id (str, opcional): ID del pedido.
#   ammount (float, opcional): Monto de la compra.
# -----------------------------------------------------------------------------
def send_email_purchase(email, order_id=None, ammount=None):
    msg = EmailMessage()
    msg['Subject'] = 'Thanks for your purchase 🚀'
    msg['From'] = os.getenv("EMAIL_FROM")
    msg['To'] = email
    content = f"""
    Dear AstroLeap Adventurer,

    Thank you for your purchase! 🌟✨
    We are thrilled to have you as part of our cosmic journey. Your support helps us continue creating stellar experiences for explorers like you.

    Your order (ID: {order_id}) for {float(ammount):.2f} USD has been received and is being processed. 🚀💸

    Get ready to leap through the stars and uncover new worlds!

    If you have any questions or need assistance, feel free to reach out to us.

    Clear skies and happy exploring! 🌠
    
    - The AstroLeap Team
    """
    msg.set_content(content)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASSWORD"))
        smtp.send_message(msg)      



# -----------------------------------------------------------------------------
# MÉTODO AUXILIAR
# Envía un correo de verificación de cuenta a un usuario nuevo.
# Parámetros:
#   email (str): Email del destinatario.
#   username (str): Nombre de usuario.
#   code (str): Código de verificación.
# -----------------------------------------------------------------------------
def send_email_simple(email, username, code):
    msg = EmailMessage()
    msg['Subject'] = '¡Welcome to AstroLeap! 🚀'
    msg['From'] = os.getenv("EMAIL_FROM")
    msg['To'] = email
    msg.set_content(f"""
    Hi {username}!

    We are thrilled to have you on board 🚀🌌
    But first, you need to verify your email to start playing AstroLeap.
    Here is your verification code: {code}

    Get ready to leap through the stars and discover new worlds! 🌠

    — The AstroLeap Team
    """)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASSWORD"))
        smtp.send_message(msg)      


# -----------------------------------------------------------------------------
# MÉTODO AUXILIAR
# Envía un correo con el código para restablecer la contraseña.
# Parámetros:
#   email (str): Email del destinatario.
#   username (str): Nombre de usuario.
#   code (str): Código de recuperación.
# -----------------------------------------------------------------------------
def send_forgot_email_code(email, username, code):
    msg = EmailMessage()
    msg['Subject'] = '🚀Did you forget your password? AstroLeap has got you covered!'
    msg['From'] = os.getenv("EMAIL_FROM")
    msg['To'] = email
    msg.set_content(f"""
    Hi {username},

    It seems like you've forgotten your password. Don't worry, we're here to help! 🚀🌌
    Here is the code to reset your password:
    Your verification code is: {code}

    Get ready to run among the stars and discover new worlds! 🌠

    — The AstroLeap Team
    """)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASSWORD"))
        smtp.send_message(msg)


