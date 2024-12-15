import requests

# Función para mostrar el menú
def mostrar_menu():
    print("\nBienvenido")
    print("\nMenú Usuario:")
    print("1. Listar Slices")
    print("2. Salir")

# Función para obtener los slices, enviando el token JWT en la cabecera
def slices(token):
    url = "http://10.20.12.187:5810/slices"
    headers = {
        "Authorization": f"Bearer {token}"  # Aquí se envía el token JWT
    }
    try:
        response = requests.get(url, headers=headers)  # Ahora usa GET en lugar de POST
        if response.status_code == 200:
            print("\nRespuesta del servidor:")
            print(response.json())
        else:
            print(f"\nError {response.status_code}: {response.json()['detail']}")
    except Exception as e:
        print(f"\nError al conectarse al servidor: {e}")

# Función principal del programa
def run(token):
    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ")
        
        if opcion == "1":
            print("Has seleccionado: Listar Slices")
            slices(token)  # Envía el token a la función slices
        elif opcion == "2":
            print("Gracias por usar el programa. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")

# Llamada al programa principal con un token como ejemplo
if __name__ == "__main__":
    # Simula un token JWT válido (reemplázalo con el token real obtenido del login)
    token = input("Por favor, introduce tu token JWT: ")
    run(token)
