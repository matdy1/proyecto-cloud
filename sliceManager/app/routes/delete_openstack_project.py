import requests
import sys
from openstack_sf import get_admin_token, get_token_for_project
from openstack_sdk import (
    list_servers,
    delete_server,
    list_ports,
    delete_port,
    list_subnets, 
    delete_subnet,
    list_networks,
    delete_network,
    delete_project,
    list_projects  # Añadimos esta importación para listar proyectos
)
import os
from dotenv import load_dotenv

load_dotenv()

KEYSTONE_ENDPOINT = f'http://{os.getenv("ACCESS_NODE_IP")}:{os.getenv("KEYSTONE_PORT")}/v3'
NOVA_ENDPOINT = f'http://{os.getenv("ACCESS_NODE_IP")}:{os.getenv("NOVA_PORT")}/v2.1'
NEUTRON_ENDPOINT = f'http://{os.getenv("ACCESS_NODE_IP")}:{os.getenv("NEUTRON_PORT")}/v2.0'

def delete_project_resources(project_id, admin_token):
    try:
        # Get project-scoped token
        project_token = get_token_for_project(project_id, admin_token)
        if not project_token:
            print("Failed to get project token")
            return False

        # Delete Instances (Servers)
        servers = list_servers(NOVA_ENDPOINT, project_token, project_id)
        if servers.status_code == 200:
            for server in servers.json()['servers']:
                delete_response = delete_server(NOVA_ENDPOINT, project_token, server['id'])
                print(f"Deleted server {server['id']}: {delete_response.status_code}")

        # Delete Ports
        ports = list_ports(NEUTRON_ENDPOINT, project_token, project_id)
        if ports.status_code == 200:
            for port in ports.json()['ports']:
                delete_response = delete_port(NEUTRON_ENDPOINT, project_token, port['id'])
                print(f"Deleted port {port['id']}: {delete_response.status_code}")

        # Delete Subnets
        subnets = list_subnets(NEUTRON_ENDPOINT, project_token, project_id)
        if subnets.status_code == 200:
            for subnet in subnets.json()['subnets']:
                delete_response = delete_subnet(NEUTRON_ENDPOINT, project_token, subnet['id'])
                print(f"Deleted subnet {subnet['id']}: {delete_response.status_code}")

        # Delete Networks
        networks = list_networks(NEUTRON_ENDPOINT, project_token, project_id)
        if networks.status_code == 200:
            for network in networks.json()['networks']:
                delete_response = delete_network(NEUTRON_ENDPOINT, project_token, network['id'])
                print(f"Deleted network {network['id']}: {delete_response.status_code}")

        return True
    except Exception as e:
        print(f"Error deleting project resources: {e}")
        return False

def delete_entire_project(project_id):
    # Get admin token
    admin_token = get_admin_token()
    if not admin_token:
        print("Failed to get admin token")
        return False

    try:
        # Primero elimina todos los recursos del proyecto
        if not delete_project_resources(project_id, admin_token):
            print("Failed to delete project resources")
            return False

        # Luego elimina el proyecto
        delete_project_response = delete_project(KEYSTONE_ENDPOINT, admin_token, project_id)
        
        if delete_project_response.status_code in [200, 204]:
            print(f"Project {project_id} deleted successfully")
            return True
        else:
            print(f"Failed to delete project. Status code: {delete_project_response.status_code}")
            return False
    except Exception as e:
        print(f"Error deleting project: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python delete_openstack_project.py <project_id>")
        sys.exit(1)

    project_id = sys.argv[1]

    try:
        # Confirmación implícita de eliminación
        print(f"Attempting to delete project with ID: {project_id}")

        response = delete_entire_project(project_id)
        if response.get("status") == "success":
            print(f"Project {project_id} deletion completed successfully.")
        else:
            print(f"Project {project_id} deletion failed: {response.get('detail')}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()