from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
import pymysql
import os
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
import mysql.connector

# Cargar las variables de entorno
load_dotenv()

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'proyectoCloud'
}

# Crear el router
router = APIRouter()

# Clave secreta para los tokens JWT (debería estar en las variables de entorno)
JWT_SECRET = os.getenv('JWT_SECRET', 'secret_key')  # Reemplaza 'secret_key' con una clave fuerte
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_MINUTES = 30

def save_log_to_db(action, project_id=None, user=None, details=None):
    """
    Guarda un registro de log en la base de datos.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Insertar el log en la tabla "logs"
        query = """
            INSERT INTO logs (action, project_id, user, details) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (action, project_id, user, details))
        connection.commit()
        print(f"Log registrado: Acción '{action}', Proyecto '{project_id}', Usuario '{user}'")
    
    except mysql.connector.Error as e:
        print(f"Error al guardar el log en la base de datos: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Definir la conexión a la base de datos MySQL
def get_db_connection():
    connection = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    return connection

# Modelo para los datos del login
class LoginData(BaseModel):
    username: str
    password: str

# Función para verificar credenciales
def check_credentials(username, password):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, nombre, rol FROM Usuarios WHERE nombre=%s AND contraseña=%s", 
        (username, password)
    )
    user = cursor.fetchone()
    connection.close()
    return user

# Función para generar un token JWT (se envía el nombre del usuario en lugar del ID)
def create_jwt_token(username, role):
    expiration = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    payload = {
        "sub": username,  # Aquí se envía el nombre del usuario
        "role": role,
        "exp": expiration
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

# Ruta para el login
@router.post('/')
def login(data: LoginData):
    username = data.username
    password = data.password

    user = check_credentials(username, password)
    if user:
        _, user_name, user_role = user  # Extraer el nombre y rol del usuario
        save_log_to_db(
            accion="Crear Slice",
            rol=user_role,
            usuario=user_name,
            detalles="Se agregó un nuevo slice a la tabla slices"
        )
        token = create_jwt_token(user_name, user_role)  # Crear el token con el nombre
        return {
            "status": "success",
            "message": "Bienvenido al sistema",
            "token": token,
            "role": user_role  # Se incluye el rol en la respuesta
        }
    else:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
