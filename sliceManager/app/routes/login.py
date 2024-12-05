from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
import pymysql
import os
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta

# Cargar las variables de entorno
load_dotenv()

# Crear el router
router = APIRouter()

# Clave secreta para los tokens JWT (debería estar en las variables de entorno)
JWT_SECRET = os.getenv('JWT_SECRET', 'secret_key')  # Reemplaza 'secret_key' con una clave fuerte
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_MINUTES = 30

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

# Función para generar un token JWT
def create_jwt_token(user_id, username, role):
    expiration = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    payload = {
        "sub": user_id,
        "username": username,
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
        user_id, user_name, user_role = user
        token = create_jwt_token(user_id, user_name, user_role)
        return {
            "status": "success",
            "message": "Bienvenido al sistema",
            "token": token,
            "role": user_role  # Se incluye el rol en la respuesta
        }
    else:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
