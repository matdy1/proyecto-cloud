from fastapi import FastAPI
from routes import login, topology, slices, monitoreo, logs # Importar los routers que has creado

app = FastAPI()

# Registrar los routers
app.include_router(login.router, prefix="/login")
app.include_router(topology.router, prefix="/topology")
app.include_router(slices.router, prefix="/slices")
app.include_router(monitoreo.router, prefix="/monitoreo")
app.include_router(logs.router, prefix="/logs")

"HOLA"

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5810)