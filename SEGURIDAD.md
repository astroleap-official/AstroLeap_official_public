# Documentación de Seguridad de la API Flask

## Resumen
Este documento describe las medidas de seguridad implementadas en la API desarrollada en Flask para el TFC. La seguridad está orientada a proteger la API frente a abusos básicos y a facilitar el desarrollo sin romper la compatibilidad con clientes existentes.

## Medidas de Seguridad Implementadas

### 1. Rate Limiting (Limitación de Peticiones)
- Se utiliza la librería `flask-limiter` para limitar el número de peticiones que puede realizar una misma IP.
- Límite global: **100 peticiones por minuto por IP**.
- Objetivo: evitar ataques de denegación de servicio (DoS) y abuso de la API.

### 2. CORS (Cross-Origin Resource Sharing)
- Se utiliza la librería `flask-cors` para permitir el acceso a la API desde cualquier origen.
- Esto facilita el desarrollo y pruebas desde diferentes clientes y entornos.
- Si se requiere mayor seguridad, se puede restringir a dominios concretos.

### 3. Middleware de Seguridad
- Antes de cada petición, se ejecuta un middleware que:
  - Registra en consola el método, ruta, IP y User-Agent de la petición.
  - Rechaza peticiones que no incluyan cabecera `User-Agent` (protección básica contra bots).

### 4. Manejo de Contraseñas
- **Actualmente, las contraseñas se almacenan ya que el haseo de estas se hace desde el cliente** para mantener la compatibilidad con el cliente existente.
- No se realiza hasheo ni cifrado de contraseñas.
- Los usuarios autenticados mediante Google tienen la contraseña especial `"NONE"` y no pueden autenticarse mediante contraseña.

### 5. Manejo de Errores
- Los errores internos del servidor no exponen información sensible al cliente.
- Se devuelve un mensaje genérico en caso de error interno.

### 6. Protección frente a Inyección SQL
- Todas las consultas a la base de datos se realizan utilizando **consultas parametrizadas** con la librería psycopg2.
- Esto impide que los datos proporcionados por el usuario puedan modificar la estructura de la consulta SQL, evitando ataques de inyección de SQL.
- Ejemplo de consulta segura:
  cur.execute('SELECT * FROM "user" WHERE email = %s', (email,))
- Recomendación: Mantener siempre el uso de parámetros en todas las consultas y evitar construir consultas SQL concatenando cadenas de texto con datos del usuario.
