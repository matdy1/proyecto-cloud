from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import networkx as nx
import paramiko
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import subprocess

router = APIRouter()

class VMData(BaseModel):
    nombre: str
    ram: int
    almacenamiento: int
    internet: bool
    worker_num: str
    worker: str
    vlan_tag: int

class TopologyData(BaseModel):
    tipo_topologia: str
    vms: List[VMData]

def ejecutar_comando_local(comando, sudo=False):
    if sudo:
        comando = f"sudo {comando}"
    try:
        result = subprocess.run(comando, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr

def conectar_ssh(hostname, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, username=username, password=password)
        return ssh
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar por SSH a {hostname}: {str(e)}")

def ejecutar_comando_ssh(ssh, comando, sudo=False):
    if sudo:
        comando = f"echo zenbook13 | sudo -S {comando}"
    stdin, stdout, stderr = ssh.exec_command(comando)
    return stdout.read().decode('utf-8'), stderr.read().decode('utf-8')

def visualizar_topologia(vms, topologia):
    G = nx.Graph()
    
    for vm in vms:
        G.add_node(vm.nombre)
    
    if topologia.lower() == "lineal":
        for i in range(len(vms) - 1):
            G.add_edge(vms[i].nombre, vms[i+1].nombre)
    
    pos = nx.spring_layout(G)
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightgreen', node_size=3000, font_size=12, font_weight='bold')
    
    node_labels = {vm.nombre: f"{vm.nombre}\nRAM: {vm.ram}GB\nStorage: {vm.almacenamiento}GB\nInternet: {'Sí' if vm.internet else 'No'}\nWorker: {vm.worker}" for vm in vms}
    nx.draw_networkx_labels(G, pos, node_labels, font_size=8)
    
    plt.title(f"Topología de Red: {topologia}")
    plt.axis('off')
    plt.tight_layout()
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return graph_url

@router.post('/create')
def create_topology(data: TopologyData):
    try:
        # Ejecutar init_headnode.sh localmente
        out, err = ejecutar_comando_local("./init_headnode.sh br-int ens5", sudo=True)
        if err:
            raise HTTPException(status_code=500, detail=f"Error al ejecutar init_headnode.sh: {err}")

        # Crear VLANs
        vlan_commands = []
        for vm in data.vms:
            ip_base = f"192.168.{vm.vlan_tag // 100}"
            vlan_commands.append(f"vlan{vm.vlan_tag} {vm.vlan_tag} {ip_base}.0/24 {ip_base}.50,{ip_base}.100")

        vlan_command = "./create_multiple_vlans.sh " + "     ".join(vlan_commands)
        out, err = ejecutar_comando_local(vlan_command, sudo=True)
        if err:
            raise HTTPException(status_code=500, detail=f"Error al crear VLANs: {err}")

        # Configurar comunicación entre VLANs para topología lineal
        if data.tipo_topologia.lower() == "lineal":
            for i in range(len(data.vms) - 1):
                vlan1 = data.vms[i].vlan_tag
                vlan2 = data.vms[i+1].vlan_tag
                out, err = ejecutar_comando_local(f"./enable_vlan_communication.sh {vlan1} {vlan2}", sudo=True)
                if err:
                    raise HTTPException(status_code=500, detail=f"Error al habilitar comunicación entre VLANs: {err}")

        # Habilitar acceso a internet para VMs seleccionadas
        for vm in data.vms:
            if vm.internet:
                out, err = ejecutar_comando_local(f"./enable_vlan_internet_access.sh {vm.vlan_tag}", sudo=True)
                if err:
                    raise HTTPException(status_code=500, detail=f"Error al habilitar acceso a internet: {err}")

        # Desplegar VMs en workers
        worker_ips = {'1': '10.0.0.30', '2': '10.0.0.40', '3': '10.0.0.50'}
        for vm in data.vms:
            worker_ip = worker_ips[vm.worker_num]
            worker_ssh = conectar_ssh(worker_ip, 'ubuntu', 'zenbook13')
            
            create_vm_command = f"./create_vm.sh {vm.nombre} br-int {vm.vlan_tag} {vm.vlan_tag // 100}"
            out, err = ejecutar_comando_ssh(worker_ssh, create_vm_command, sudo=True)
            if err:
                worker_ssh.close()
                raise HTTPException(status_code=500, detail=f"Error al crear VM: {err}")
            
            init_worker_command = "./init_worker.sh br-int ens4"
            out, err = ejecutar_comando_ssh(worker_ssh, init_worker_command, sudo=True)
            if err:
                worker_ssh.close()
                raise HTTPException(status_code=500, detail=f"Error al inicializar worker: {err}")
            
            worker_ssh.close()

        # Generar visualización de la topología
        graph_url = visualizar_topologia(data.vms, data.tipo_topologia)

        return {
            "message": f"Topología {data.tipo_topologia} creada exitosamente",
            "topology": {
                "tipo": data.tipo_topologia,
                "vms": [vm.dict() for vm in data.vms],
                "graph": graph_url
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la topología: {str(e)}")