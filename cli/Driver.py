import os

def mostrar_menu():
    print("Elija donde desplegar los slices:")
    print("1. Linux")
    print("2. OpenStack")

def run(token):
    while True:
        mostrar_menu()
        opcion = input("Ingrese el número de su opción (o 'q' para salir): ").strip()

        if opcion == '1':
            print("Ejecutando script para Linux...")
            import Crear_Slices
            Crear_Slices.crear_topologia(token)
        elif opcion == '2':
            print("ESjecutando script para OpenStack...")
            import Crear_Slices_OP
            Crear_Slices_OP.run(token)
        elif opcion.lower() == 'q':
            print("Saliendo del programa. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")
