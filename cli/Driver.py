import os

def mostrar_menu():
    print("Elija donde desplegar los slices:")
    print("1. Linux")
    print("2. OpenStack")

def run():
    while True:
        mostrar_menu()
        opcion = input("Ingrese el número de su opción (o 'q' para salir): ").strip()

        if opcion == '1':
            print("Ejecutando script para Linux...")
            os.system("python3 Crear_Slices.py")
        elif opcion == '2':
            print("Ejecutando script para OpenStack...")
            os.system("python3 Crear_Slices_OP.py")
        elif opcion.lower() == 'q':
            print("Saliendo del programa. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    run()
