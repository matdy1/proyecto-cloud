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
    print("5. Salir")

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
            print("Gracias por usar el programa. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")
