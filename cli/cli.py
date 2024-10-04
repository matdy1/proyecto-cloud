import requests
import getpass

# Solicitar credenciales al usuario
username = input("Por favor, introduce tu nombre de usuario: ")
password = getpass.getpass("Por favor, introduce tu contraseña: ")

# URL del servidor FastAPI
url = "http://127.0.0.1:8000/login"

# Datos de login
data = {
    "username": username,
    "password": password
}

# Realizar la solicitud POST al servidor FastAPI
try:
    response = requests.post(url, json=data)
    
    # Comprobar la respuesta del servidor
    if response.status_code == 200:
        print("¡Login exitoso!")
        print("Respuesta del servidor:", response.json())
    else:
        print("Error de login:", response.status_code)
        print("Detalles:", response.text)

except requests.ConnectionError:
    print("Error: No se pudo conectar al servidor.")
