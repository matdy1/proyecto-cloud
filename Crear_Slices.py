import subprocess

def mostrar_opciones_topologia():
    print("\nOpciones de Topología:")
    print("1. Lineal")
    print("2. Anillo")
    print("3. Bus")
    print("4. Árbol")

def crear_topologia():
    while True:
        mostrar_opciones_topologia()
        opcion = input("\nSelecciona una topología: ")
        
        if opcion in ["1", "2", "3", "4"]:
            topologias = {
                "1": "Lineal",
                "2": "Anillo",
                "3": "Bus",
                "4": "Árbol"
            }
            print(f"Has seleccionado la topología {topologias[opcion]}")
            subprocess.run(["python", "Lineal.py", topologias[opcion]])
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")

if __name__ == "__main__":
    print("Bienvenido a la creación de topologías para Slices")
    crear_topologia()
    input("Presiona Enter para volver al menú principal...")