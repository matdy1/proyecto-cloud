import sys
import requests
from typing import List, Dict
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def recopilar_datos_vms() -> List[Dict]:
    vms = []
    num_vms = int(input("Ingrese número de máquinas virtuales (VM): "))
    
    for i in range(1, num_vms + 1):
        print(f"\nConfiguración para VM{i}:")
        ram = int(input(f"Cantidad de RAM (GB) para la VM{i}: "))
        storage = int(input(f"Cantidad de almacenamiento (GB) para la VM{i}: "))
        internet = input(f"¿Desea que la VM{i} tenga conexión a internet? (s/n): ").lower() == 's'
        worker_num = input('Selecciona un worker (1-3): ')
        worker = f"Worker {worker_num}"

        vms.append({
            "nombre": f"VM{i}",
            "ram": ram,
            "almacenamiento": storage,
            "internet": internet,
            "worker": worker,
            "worker_num": worker_num,
            "vlan_tag": i * 100
        })
    
    return vms

def enviar_datos_a_endpoint(tipo_topologia: str, vms: List[Dict]):
    url = "http://10.20.12.106:5810/create_topology"
    
    payload = {
        "tipo_topologia": tipo_topologia,
        "vms": vms
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar datos: {e}")
        return None

def mostrar_topologia(graph_url: str):
    img_data = base64.b64decode(graph_url)
    img = BytesIO(img_data)
    plt.imshow(plt.imread(img))
    plt.axis('off')
    plt.show()

def main(tipo_topologia: str):
    print(f"\nConfiguración de VMs para topología {tipo_topologia}")
    
    vms = recopilar_datos_vms()
    
    respuesta = enviar_datos_a_endpoint(tipo_topologia, vms)
    
    if respuesta:
        print("\nTopología creada exitosamente en el servidor.")
        print("\nVisualización de la topología:")
        mostrar_topologia(respuesta['topology']['graph'])
        
        print("\nResumen de la configuración:")
        print(f"Topología: {respuesta['topology']['tipo']}")
        for vm in respuesta['topology']['vms']:
            print(f"\n{vm['nombre']}:")
            print(f"  RAM: {vm['ram']} GB")
            print(f"  Almacenamiento: {vm['almacenamiento']} GB")
            print(f"  Conexión a internet: {'Sí' if vm['internet'] else 'No'}")
            print(f"  Desplegada en: {vm['worker']}")
            print(f"  VLAN tag: {vm['vlan_tag']}")
    else:
        print("No se pudo crear la topología en el servidor.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Error: No se especificó el tipo de topología. Use: python script.py <tipo_topologia>")