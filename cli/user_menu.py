def mostrar_menu():
    print("\nBienvenido")
    print("\nMenú Usuario:")
    print("1. Listar Slices")
    print("2. Salir")

def run(token):
    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ")
        
        if opcion == "1":
            print("Has seleccionado: Listar Slices")
            # Aquí puedes implementar lógica adicional, por ejemplo, usar el token para una solicitud API.
        elif opcion == "2":
            print("Gracias por usar el programa. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")
