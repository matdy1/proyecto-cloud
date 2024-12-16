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

# Endpoint para obtener todos los datos de worker_metrics
@router.get("/")
async def get_worker_metrics():
    try:
        # Conexión a la base de datos
        with mysql.connector.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                # Consulta para obtener todos los datos
                query = """
                SELECT worker_ip, average_cpu_usage, average_total_ram,
                       average_used_ram, average_free_ram, timestamp
                FROM worker_metrics
                """
                cursor.execute(query)
                results = cursor.fetchall()

                # Verificar si hay datos
                if not results:
                    raise HTTPException(status_code=404, detail="No hay datos disponibles.")

                # Crear una lista de diccionarios con los datos
                workers = [
                    {
                        "worker_ip": row[0],
                        "average_cpu_usage": row[1],
                        "average_total_ram": row[2],
                        "average_used_ram": row[3],
                        "average_free_ram": row[4],
                        "timestamp": row[5]
                    }
                    for row in results
                ]

                # Devolver los datos formateados en JSON
                return {"users": workers}

    except Error as db_error:
        print(f"Error: {db_error}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
