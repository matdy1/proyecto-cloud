from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymysql
import os
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

app = FastAPI()

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
    cursor.execute("SELECT * FROM Usuarios WHERE nombre=%s AND contraseña=%s", (username, password))
    user = cursor.fetchone()
    connection.close()
    return user

# Ruta para el login
@app.post('/login')
def login(data: LoginData):
    username = data.username
    password = data.password

    if check_credentials(username, password):
        return {"status": "success", "message": "Bienvenido al sistema"}
    else:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5810)
