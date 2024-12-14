import subprocess

def mostrar_opciones_topologia():
    print("\nOpciones de Topología:")
    print("1. Lineal")
    print("2. Anillo")
    print("3. Parcial")
    print("4. Perzonalizado")

def obtener_parametros_topologia(nombre_topologia):
    """Solicita al usuario el nombre y número de nodos para la topología especificada."""
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

def run():
    while True:
        mostrar_opciones_topologia()
        opcion = input("\nSelecciona una topología: ").strip()

        if opcion in ["1", "2", "3", "4"]:
            topologias = {
                "1": "Lineal_OP",
                "2": "Anillo_OP",
                "3": "Parcial",
                "4": "Perzonalizado"
            }
            script_name = f"{topologias[opcion]}.py"

            # Configurar parámetros adicionales según la topología
            if opcion in ["1", "2"]:
                # Solicitar parámetros para las topologías lineal y anillo
                nombre, num_nodos = obtener_parametros_topologia(topologias[opcion])
                parametros = [nombre, str(num_nodos)]
            else:
                parametros = [topologias[opcion]]

            print(f"Has seleccionado la topología {topologias[opcion]}")
            try:
                # Ejecuta el script con los parámetros adecuados
                subprocess.run(["python", script_name] + parametros, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error al ejecutar el script {script_name}: {e}")
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")

if __name__ == "__main__":
    print("Bienvenido a la creación de topologías para Slices")
    run()
    input("Presiona Enter para volver al menú principal...")
