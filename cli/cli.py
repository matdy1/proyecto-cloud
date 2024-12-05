import requests
import getpass

# Solicitar credenciales al usuario
username = input("Por favor, introduce tu nombre de usuario: ")
password = getpass.getpass("Por favor, introduce tu contraseña: ")

# URL del servidor FastAPI
url = "http://10.20.12.187:5810/login"

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
        
        # Extraer la respuesta JSON
        server_response = response.json()
        token = server_response.get("token")
        role = server_response.get("role")
        
        print(f"Token: {token}")
        print(f"Rol: {role}")

        # Acciones según el rol del usuario
        if role == "admin":
            print("\nAccediendo al menú de administrador...")
            # Llama al script o función del menú de administrador
            import admin_menu
            admin_menu.run(token)  # Pasamos el token si es necesario
        elif role == "usuario":
            print("\nAccediendo al menú de usuario...")
            # Llama al script o función del menú de usuario
            import user_menu
            user_menu.run(token)  # Pasamos el token si es necesario
        else:
            print("Rol desconocido, cerrando sesión.")
    else:
        print("Error de login:", response.status_code)
        print("Detalles:", response.text)

except requests.ConnectionError:
    print("Error: No se pudo conectar al servidor.")
