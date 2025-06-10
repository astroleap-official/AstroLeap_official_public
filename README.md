# AstroLeap API

AstroLeap API es una plataforma backend desarrollada en Python con Flask, diseñada para gestionar la lógica de un sistema multijugador, tienda virtual, usuarios y pagos en línea. Este proyecto es parte de una tesis universitaria y está documentado para facilitar su comprensión, mantenimiento y presentación académica.

---

## Índice

- [Descripción General](#descripción-general)
- [Arquitectura del Proyecto](#arquitectura-del-proyecto)
- [Principales Endpoints](#principales-endpoints)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Despliegue y Ejecución](#despliegue-y-ejecución)
- [Ejemplo de Uso](#ejemplo-de-uso)
- [Créditos y Reconocimientos](#créditos-y-reconocimientos)

---

## Descripción General

AstroLeap API proporciona servicios RESTful para la gestión de usuarios, partidas multijugador, tienda virtual, sistema competitivo y pagos mediante PayPal. Su diseño modular permite una fácil extensión y mantenimiento, siguiendo buenas prácticas de desarrollo y documentación.

---

## Arquitectura del Proyecto

El proyecto está organizado en módulos independientes mediante Blueprints de Flask:

- **users/**: Gestión de usuarios y autenticación.
- **users_unlocks/**: Desbloqueo de logros y recompensas.
- **shop/**: Lógica de la tienda virtual.
- **user_competitive/**: Sistema competitivo y rankings.
- **multiplayer/**: Partidas multijugador y lógica de juego.
- **paypal/**: Integración de pagos y callbacks de PayPal.
- **emailSend/**: Envío de correos electrónicos automáticos.
- **current_shop/** y **user_shop/**: Gestión avanzada de inventario y compras.

El archivo principal `app.py` inicializa la aplicación, registra los Blueprints y gestiona la conexión a la base de datos.

```text
app.py
├── users/
├── users_unlocks/
├── shop/
├── user_competitive/
├── multiplayer/
├── paypal/
├── emailSend/
├── current_shop/
└── user_shop/
```

---

## Principales Endpoints

A continuación se resumen los endpoints más relevantes y representativos de la API. Para detalles completos, consulte la documentación en el código fuente y los comentarios de cada módulo.

| Módulo              | Endpoint                                 | Método   | Descripción                                      |
|---------------------|------------------------------------------|----------|--------------------------------------------------|
| users               | `/get-users`                             | GET      | Listar todos los usuarios                        |
| users               | `/get-user-by-email/<email>`             | GET      | Obtener usuario por email                        |
| users               | `/add-user`                              | POST     | Crear nuevo usuario                              |
| users_unlocks       | `/get-user-unlocks/<user_id>`            | GET      | Obtener desbloqueos de usuario                   |
| users_unlocks       | `/add-user-unlocks`                      | POST     | Añadir desbloqueos a usuario                     |
| shop                | `/get-shop`                              | GET      | Listar ítems de la tienda                        |
| shop                | `/add-shop-item`                         | POST     | Añadir ítem a la tienda                          |
| multiplayer         | `/rooms/first-available`                 | GET      | Buscar sala multijugador disponible              |
| multiplayer         | `/rooms`                                 | POST     | Crear nueva sala multijugador                    |
| user_competitive    | `/user_competitive/<id_user>`            | GET      | Obtener datos competitivos de usuario            |
| user_competitive    | `/user_competitive`                      | POST     | Crear registro competitivo                       |
| user_shop           | `/user_shop/<id_user>`                   | GET      | Obtener ofertas de usuario                       |
| current_shop        | `/current_shop`                          | GET      | Listar id_shop actuales                          |
| current_shop        | `/current_shop`                          | POST     | Añadir id_shop a la tienda actual                |
| paypal              | `/paypal/create-payment`                  | POST     | Iniciar pago con PayPal                          |
| paypal              | `/paypal/success`                        | GET      | Callback de pago exitoso                         |
| emailSend           | `/send-email`                            | POST     | Enviar correo electrónico                        |

---

## Tecnologías Utilizadas

- **Python 3.10+**
- **Flask** (microframework web)
- **Flask Blueprints** (modularidad)
- **SQLite/MySQL** (según configuración)
- **PayPal REST SDK** (pagos en línea)
- **Jinja2** (plantillas HTML)
- **gunicorn** (despliegue en producción)

---

## Despliegue y Ejecución

### Requisitos previos

- Python 3.10 o superior
- pip (gestor de paquetes)

### Instalación

```bash
pip install -r requirements.txt
```

### Ejecución local

```bash
python app.py
```

La API estará disponible en `http://localhost:5000`.

### Despliegue en producción (ejemplo con Gunicorn)

```bash
gunicorn app:app
```

---

## Ejemplo de Uso

### Registro de usuario

```bash
curl -X POST http://localhost:5000/users/register \
     -H "Content-Type: application/json" \
     -d '{"username": "astro", "password": "leap123"}'
```

### Respuesta esperada

```json
{
  "status": "success",
  "message": "Usuario registrado correctamente."
}
```

---

## Créditos y Reconocimientos

- **Autor:** Álvaro Blanco
- **Colegio:** Colegio Santa Gema Galgani
- **Tesis dirigida por:** Jose Antonio Redondo
- **Agradecimientos:** A la comunidad de Flask y a todos los colaboradores.