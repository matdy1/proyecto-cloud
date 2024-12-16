from tabulate import tabulate
def mostrar_menu():
    print("""
    
     ██████╗██╗      ██████╗ ██╗   ██╗██████╗ 
    ██╔════╝██║     ██╔═══██╗██║   ██║██╔══██╗
    ██║     ██║     ██║   ██║██║   ██║██║  ██║
    ██║     ██║     ██║   ██║██║   ██║██║  ██║
    ╚██████╗███████╗╚██████╔╝╚██████╔╝██████╔╝
     ╚═════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ 
    """)
    print("\n¡Bienvenido al Sistema de Gestión de Slices!")
    print("\nMenú Administrador:")
    print("1. Listar Slices")
    print("2. Crear Slices")
    print("3. Editar Slices")
    print("4. Borrar Slices")
    print("5. Ver recursos")
    print("5. Ver logs")
    print("6. Salir")

# Función para listar slices
import subprocess

def listar_slices():
    print("Has seleccionado: Listar Slices")
    subprocess.run(["python", "Listar_Slices.py"])

# Función para crear slices
def crear_slices(token):
    print("Has seleccionado: Crear Slices")
    import Driver
    Driver.run(token)
    # Si prefieres usar subprocess:
    # subprocess.run(["python", "Crear_Slices.py"])
    

# Función para editar slices
def editar_slices():
    print("Has seleccionado: Editar Slices")
    # Implementa aquí la lógica para editar slices
    slice_id = input("Introduce el ID del Slice a editar: ")
    print(f"Editando Slice con ID: {slice_id}")

# Función para borrar slices
def borrar_slices():
    print("Has seleccionado: Borrar Slices")
    import Delete
    Delete.main()

def monitoreo():
    url = "http://10.20.12.187:5810/monitoreo"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            users = response.json().get("users", [])
            if users:
                print("\nRecursos")
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
    
def logs():
    url = "http://10.20.12.187:5810/logs"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logs = response.json().get("logs", [])
            if logs:
                print("\n==== Registros de Logs ====\n")
                
                # Construir la tabla
                table_data = []
                for log in logs:
                    table_data.append([
                        log.get("id", "N/A"),
                        log.get("action", "N/A"),
                        log.get("project_id", "N/A"),
                        log.get("user", "N/A"),
                        log.get("timestamp", "N/A"),
                        log.get("details", "N/A")
                    ])
                
                # Encabezados
                headers = ["ID", "Acción", "ID Proyecto", "Usuario", "Fecha/Hora", "Detalles"]
                
                # Mostrar la tabla con tabulate
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                return logs
            else:
                print("No hay registros de logs disponibles.")
                return []
        else:
            print(f"Error al consultar los logs: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error al conectarse al servidor: {e}")
        return []    

# Función principal del menú
def run(token):
    print(f"\nTu token es: {token}")  # Mostrar el token para referencia, si es necesario.
    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ")
        
        if opcion == "1":
            listar_slices()
        elif opcion == "2":
            crear_slices(token)
        elif opcion == "3":
            editar_slices()
        elif opcion == "4":
            borrar_slices()
        elif opcion == "5":
            monitoreo()
        elif opcion == "5":
            logs()       
        elif opcion == "6":
            print("Gracias por usar el programa. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")
