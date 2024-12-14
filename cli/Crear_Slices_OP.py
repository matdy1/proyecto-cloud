import requests

def mostrar_opciones_topologia():
    print("\nOpciones de Topología:")
    print("1. Lineal")
    print("2. Anillo")

def obtener_parametros_topologia(topology_type):
    nombre = input(f"Ingrese el nombre de la topología ({topology_type}): ").strip()
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

def obtener_usuarios_disponibles():
    url = "http://10.20.12.187:5810/topology/create"
    data = {"num_nodes": 2, "topology_name": "dummy", "topology_type": "lineal"}  # Datos temporales
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            usuarios = response.json().get("usuarios_disponibles", [])
            if usuarios:
                print("\nUsuarios disponibles:")
                for i, usuario in enumerate(usuarios, start=1):
                    print(f"{i}. {usuario}")
                return usuarios
            else:
                print("No hay usuarios disponibles.")
                return []
        else:
            print(f"Error al obtener usuarios: {response.status_code}")
            print(response.json())
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
            print("Topología creada exitosamente.")
            print("Respuesta del servidor:")
            print(response.json())
        else:
            print(f"Error: {response.status_code}")
            print(response.json())
    except Exception as e:
        print(f"Error al conectarse al servidor: {e}")

def run():
    while True:
        mostrar_opciones_topologia()
        opcion = input("\nSelecciona una topología: ").strip()

        if opcion == "1":
            topology_type = "lineal"
        elif opcion == "2":
            topology_type = "anillo"
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")
            continue

        nombre, num_nodos = obtener_parametros_topologia(topology_type)
        usuarios = obtener_usuarios_disponibles()

        if not usuarios:
            print("No se puede continuar sin usuarios disponibles.")
            continue

        # Seleccionar un usuario
        while True:
            try:
                seleccion = int(input("Selecciona un usuario por número: ").strip())
                if 1 <= seleccion <= len(usuarios):
                    selected_user = usuarios[seleccion - 1]
                    break
                else:
                    print("Número fuera de rango. Intenta de nuevo.")
            except ValueError:
                print("Por favor, ingresa un número válido.")

        enviar_solicitud_topologia(nombre, num_nodos, topology_type, selected_user)

if __name__ == "__main__":
    print("Bienvenido a la creación de topologías para Slices")
    run()
