def mostrar_menu():
    print("\nBienvenido")
    print("\nMenú Administrador:")
    print("1. Listar Slices")
    print("2. Crear Slices")
    print("3. Editar Slices")
    print("4. Borrar Slices")
    print("5. Salir")

# Función para listar slices
def listar_slices():
    print("Has seleccionado: Listar Slices")
    # Aquí puedes implementar la lógica para listar slices
    # Por ejemplo, obtener datos desde un servidor o base de datos.

# Función para crear slices
def crear_slices():
    print("Has seleccionado: Crear Slices")
    import Driver
    Driver.run()
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
    # Implementa aquí la lógica para borrar slices
    slice_id = input("Introduce el ID del Slice a borrar: ")
    print(f"Borrando Slice con ID: {slice_id}")

# Función principal del menú
def run(token):
    print(f"\nTu token es: {token}")  # Mostrar el token para referencia, si es necesario.
    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ")
        
        if opcion == "1":
            listar_slices()
        elif opcion == "2":
            crear_slices()
        elif opcion == "3":
            editar_slices()
        elif opcion == "4":
            borrar_slices()
        elif opcion == "5":
            print("Gracias por usar el programa. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")
