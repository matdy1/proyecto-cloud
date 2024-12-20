import subprocess

def mostrar_opciones_topologia():
    print("\nOpciones de Topología:")
    print("1. Lineal")
    print("2. Anillo")
    print("3. Parcial")
    print("4. Perzonalizado")
    print("5. Salir")

def crear_topologia():
    while True:
        mostrar_opciones_topologia()
        opcion = input("\nSelecciona una topología o salir: ")
        
        if opcion in ["1", "2", "3", "4","5"]:
            if opcion == "5":
                subprocess.run(["python3", "Driver.py"])
                return
            
            topologias = {
                "1": "Lineal",
                "2": "Anillo",
                "3": "Parcial",
                "4": "Perzonalizado"
            }
            script_name = f"{topologias[opcion]}.py"
            print(f"Has seleccionado la topología {topologias[opcion]}")
            try:
                # Pasa la topología como argumento
                subprocess.run(["python", script_name, topologias[opcion]], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error al ejecutar el script {script_name}: {e}")
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")

if __name__ == "__main__":
    print("Bienvenido a la creación de topologías para Slices")
    crear_topologia()
    input("Presiona Enter para finalizar...")