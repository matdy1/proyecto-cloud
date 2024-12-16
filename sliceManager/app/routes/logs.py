import mysql.connector
from mysql.connector import Error
from fastapi import APIRouter, HTTPException

# Definir el router
router = APIRouter()

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'proyectoCloud'
}

# Endpoint para obtener todos los datos de la tabla logs
@router.get("/")
async def get_logs():
    try:
        # Conexión a la base de datos
        with mysql.connector.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                # Consulta para obtener todos los datos de la tabla logs
                query = """
                SELECT id, action, project_id, user, timestamp, details
                FROM logs
                """
                cursor.execute(query)
                results = cursor.fetchall()

                # Verificar si hay datos
                if not results:
                    raise HTTPException(status_code=404, detail="No hay datos disponibles.")

                # Crear una lista de diccionarios con los datos
                logs = [
                    {
                        "id": row[0],
                        "action": row[1],
                        "project_id": row[2],
                        "user": row[3],
                        "timestamp": row[4],
                        "details": row[5]
                    }
                    for row in results
                ]

                # Devolver los datos formateados en JSON
                return {"logs": logs}

    except Error as db_error:
        print(f"Error: {db_error}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
