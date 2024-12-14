import requests

def mostrar_opciones_topologia():
    print("\nOpciones de Topología:")
    print("1. Lineal")
    print("2. Anillo")

def obtener_parametros_topologia(nombre_topologia):
    nombre = input(f"Ingrese el nombre de la topología ({nombre_topologia}): ").strip()
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

def enviar_solicitud_topologia(topology_name, num_nodes, topology_type):
    url = "http://10.20.12.187:5810/topology/create"
    data = {
        "topology_name": topology_name,
        "num_nodes": num_nodes,
        "topology_type": topology_type
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

        if opcion in ["1", "2"]:
            topologias = {
                "1": "lineal",
                "2": "anillo"
            }
            topology_type = topologias[opcion]
            nombre, num_nodos = obtener_parametros_topologia(topology_type)
            enviar_solicitud_topologia(nombre, num_nodos, topology_type)
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")

if __name__ == "__main__":
    print("Bienvenido a la creación de topologías para Slices")
    run()
