import os
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import subprocess
import mysql.connector
from mysql.connector import Error

# Definir el router
router = APIRouter()

# Modelo de datos para las solicitudes
class TopologyRequest(BaseModel):
    topology_name: str
    num_nodes: int
    topology_type: str  # "lineal" o "anillo"
    image_id: Optional[str] = None
    flavor_id: Optional[str] = None
    selected_user: str  # Usuario seleccionado por el admin

# IDs por defecto
DEFAULT_IMAGE_ID = "4f0d4d09-d6bc-4a65-8ce2-1a181fa3e458"
DEFAULT_FLAVOR_ID = "cdd2dc7f-b00b-483d-a104-4cea575c9b1b"

# Ruta base donde están los scripts
BASE_SCRIPT_PATH = os.path.join(os.path.dirname(__file__))

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'proyectoCloud'
}

# Locks para controlar concurrencia
lock_create_topology = asyncio.Lock()
lock_get_users = asyncio.Lock()

@router.get("/users")
async def get_users():
    """
    Endpoint para obtener la lista de usuarios disponibles con rol 'usuario'.
    """
    if lock_get_users.locked():
        raise HTTPException(
            status_code=423,
            detail="El endpoint '/users' está en uso. Inténtalo de nuevo más tarde."
        )

    async with lock_get_users:
        try:
            # Conectar a la base de datos
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            # Consultar usuarios disponibles con rol "usuario"
            cursor.execute("SELECT nombre FROM Usuarios WHERE rol='usuario'")
            users = cursor.fetchall()

            if not users:
                raise HTTPException(status_code=404, detail="No hay usuarios disponibles con rol 'usuario'.")

            # Normalizar lista de usuarios
            user_list = [user[0].strip() for user in users]
            return {"users": user_list}

        except mysql.connector.Error as db_error:
            raise HTTPException(status_code=500, detail=f"Error de base de datos: {db_error}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

@router.post("/create")
async def create_topology(request: TopologyRequest):
    """
    Endpoint para crear una topología lineal o de anillo.
    """
    if request.num_nodes < 2:
        raise HTTPException(status_code=400, detail="El número de nodos debe ser al menos 2.")

    if lock_create_topology.locked():
        raise HTTPException(
            status_code=423,
            detail="El endpoint '/create' está en uso. Inténtalo de nuevo más tarde."
        )

    async with lock_create_topology:
        try:
            # Conectar a la base de datos
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            # Validar usuario seleccionado
            cursor.execute("SELECT nombre FROM Usuarios WHERE rol='usuario'")
            users = cursor.fetchall()
            user_list = [user[0].strip() for user in users]

            if request.selected_user.strip() not in user_list:
                raise HTTPException(
                    status_code=400,
                    detail=f"Usuario seleccionado no válido. Opciones: {user_list}"
                )

            selected_user = request.selected_user.strip()
            print(f"Usuario seleccionado: {selected_user}")

            # Determinar qué script ejecutar
            if request.topology_type.lower() == "lineal":
                script_path = os.path.join(BASE_SCRIPT_PATH, "Lineal_OP.py")
            elif request.topology_type.lower() == "anillo":
                script_path = os.path.join(BASE_SCRIPT_PATH, "Anillo_OP.py")
            else:
                raise HTTPException(status_code=400, detail="Tipo de topología no válida. Usa 'lineal' o 'anillo'.")

            # Parámetros de la llamada al script
            image_id = request.image_id if request.image_id else DEFAULT_IMAGE_ID
            flavor_id = request.flavor_id if request.flavor_id else DEFAULT_FLAVOR_ID

            # Ejecutar el script de topología con subprocess
            result = subprocess.run(
                ["python3", script_path, request.topology_name, str(request.num_nodes), image_id, flavor_id, selected_user],
                text=True,
                capture_output=True,
                check=True
            )

            # Capturar la salida del script
            output = result.stdout
            return {"message": "Topología creada exitosamente", "output": output}

        except mysql.connector.Error as db_error:
            raise HTTPException(status_code=500, detail=f"Error de base de datos: {db_error}")
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Error al ejecutar el script: {e.stderr}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

# Endpoint para borrar un registro de la tabla slices por idProyecto
@router.delete("/borrar/{id_proyecto}")
async def delete_slice(id_proyecto: str):
    try:
        # Conexión a la base de datos
        with mysql.connector.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                # Consulta para eliminar un registro de la tabla slices
                query = """
                DELETE FROM slices WHERE idProyecto = %s
                """
                cursor.execute(query, (id_proyecto,))
                connection.commit()

                # Verificar si se borró alguna fila
                if cursor.rowcount == 0:
                    raise HTTPException(status_code=404, detail="No se encontró el proyecto con el id proporcionado.")

                return {"message": "Registro eliminado correctamente."}

    except Error as db_error:
        print(f"Error: {db_error}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")