import os
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
import mysql.connector
import jwt

# Definir el router
router = APIRouter()

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'proyectoCloud'
}

# Clave secreta para decodificar el token JWT
JWT_SECRET = os.getenv("JWT_SECRET", "secret_key")
JWT_ALGORITHM = "HS256"

# Función para decodificar el token JWT
def decode_jwt_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    
    token = authorization.split("Bearer ")[-1]  # Extraer el token del encabezado
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload  # Retorna el payload completo del token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Endpoint para obtener los slices del usuario autenticado
@router.get("/")
async def get_slices(user: dict = Depends(decode_jwt_token)):
    """
    Endpoint para obtener la lista de slices asociados al usuario autenticado.
    """
    username = user.get("sub")  # Extraer el nombre del usuario del token JWT
    
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Consultar los slices pertenecientes al usuario autenticado
<<<<<<< HEAD
        query = "SELECT idProyecto FROM slices WHERE usuario = %s"
=======
        query = "SELECT * FROM slices WHERE usuario = %s"
>>>>>>> fd0bf2d4f975b4d3bd99d815ee989679909cdd89
        cursor.execute(query, (username,))
        slices = cursor.fetchall()

        if not slices:
            raise HTTPException(status_code=404, detail=f"No hay slices disponibles para el usuario '{username}'.")

        # Normalizar la lista de slices
<<<<<<< HEAD
        slice_list = [str(slice[0]).strip() for slice in slices]
=======
        slice_list = [slice[0].strip() for slice in slices]
>>>>>>> fd0bf2d4f975b4d3bd99d815ee989679909cdd89
        return {"user": username, "slices": slice_list}

    except mysql.connector.Error as db_error:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {db_error}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
