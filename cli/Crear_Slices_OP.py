import requests
import admin_menu  # Importar el script externo

def mostrar_opciones_topologia():
    print("\nOpciones de Topología:")
    print("1. Lineal")
    print("2. Anillo")
    print("3. Regresar")

def obtener_parametros_topologia(topology_type):
    nombre = input(f"Ingrese el nombre del proyecto ({topology_type}): ").strip()
    while True:
        try:
            num_nodos = int(input("Ingrese el número de nodos: ").strip())
            if num_nodos > 0:
                break
            else:
                print("El número de nodos debe ser un entero positivo.")
        except ValueError:
            print("Por favor, ingrese un número válido.")
    return nombre, num_nodos

def consultar_usuarios_disponibles():
    url = "http://10.20.12.187:5810/topology/users"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            users = response.json().get("users", [])
            if users:
                print("\nUsuarios disponibles:")
                for idx, user in enumerate(users, start=1):
                    print(f"{idx}. {user}")
                return users
            else:
                print("No hay usuarios disponibles.")
                return []
        else:
            print(f"Error al consultar usuarios: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error al conectarse al servidor: {e}")
        return []

def enviar_solicitud_topologia(topology_name, num_nodes, topology_type, selected_user):
    url = "http://10.20.12.187:5810/topology/create"
    data = {
        "topology_name": topology_name,
        "num_nodes": num_nodes,
        "topology_type": topology_type,
        "selected_user": selected_user
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("\nTopología creada exitosamente.")
            print("Respuesta del servidor:")
            print(response.json())
        else:
            print(f"Error: {response.status_code}")
            print(response.json())
    except Exception as e:
        print(f"Error al conectarse al servidor: {e}")

def run(token):
    while True:
        mostrar_opciones_topologia()
        opcion = input("\nSelecciona una topología: ").strip()

        if opcion == "1":
            topology_type = "lineal"
        elif opcion == "2":
            topology_type = "anillo"
        elif opcion == "3":
            print("\nRegresando al menú de administración...\n")
            import admin_menu
            admin_menu.run(token)  # Llama a la función principal del script admin_menu.py
            return  # Finaliza la ejecución del menú actual
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")
            continue

        nombre, num_nodos = obtener_parametros_topologia(topology_type)
        usuarios = consultar_usuarios_disponibles()
        
        if not usuarios:
            print("No hay usuarios para continuar. Intenta más tarde.")
            return

        while True:
            try:
                usuario_idx = int(input("\nSeleccione un usuario por su número: ").strip())
                if 1 <= usuario_idx <= len(usuarios):
                    selected_user = usuarios[usuario_idx - 1]
                    break
                else:
                    print("Número de usuario fuera de rango.")
            except ValueError:
                print("Por favor, ingrese un número válido.")

        enviar_solicitud_topologia(nombre, num_nodos, topology_type, selected_user)

if __name__ == "__main__":
    print("Bienvenido a la creación de topologías para Slices")
    run()
