from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import subprocess
import json

# Definir el router
router = APIRouter()

# Modelo de datos para las solicitudes
class TopologyRequest(BaseModel):
    topology_name: str
    num_nodes: int
    topology_type: str  # "lineal" o "anillo"
    image_id: Optional[str] = None
    flavor_id: Optional[str] = None

# IDs por defecto
DEFAULT_IMAGE_ID = "4f0d4d09-d6bc-4a65-8ce2-1a181fa3e458"
DEFAULT_FLAVOR_ID = "cdd2dc7f-b00b-483d-a104-4cea575c9b1b"

@router.post("/create")
async def create_topology(request: TopologyRequest):
    """
    Endpoint para crear una topología lineal o de anillo.
    """
    if request.num_nodes < 2:
        raise HTTPException(status_code=400, detail="El número de nodos debe ser al menos 2.")
    
    # Determinar qué script ejecutar
    if request.topology_type.lower() == "lineal":
        script_name = "Lineal_OP.py"
    elif request.topology_type.lower() == "anillo":
        script_name = "Anillo_OP.py"
    else:
        raise HTTPException(status_code=400, detail="Tipo de topología no válida. Usa 'lineal' o 'anillo'.")
    
    # Parámetros de la llamada al script
    image_id = request.image_id if request.image_id else DEFAULT_IMAGE_ID
    flavor_id = request.flavor_id if request.flavor_id else DEFAULT_FLAVOR_ID
    
    try:
        # Ejecutar el script de topología con subprocess
        result = subprocess.run(
            ["python3", script_name, request.topology_name, str(request.num_nodes), image_id, flavor_id],
            text=True,
            capture_output=True,
            check=True
        )
        # Capturar la salida del script
        output = result.stdout
        return {"message": "Topología creada exitosamente", "output": output}
    except subprocess.CalledProcessError as e:
        # Capturar errores
        raise HTTPException(status_code=500, detail=f"Error al ejecutar el script: {e.stderr}")
