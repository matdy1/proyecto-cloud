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
    # Get admin token
    admin_token = get_admin_token()
    if not admin_token:
        print("Failed to get admin token")
        return

    # List projects
    projects_response = list_projects(KEYSTONE_ENDPOINT, admin_token)
    
    if projects_response.status_code != 200:
        print("Failed to retrieve projects")
        return

    # Parse and display projects
    projects = projects_response.json().get('projects', [])
    
    print("\nAvailable Projects:")
    print("-" * 50)
    print("No. | Project ID | Project Name")
    print("-" * 50)
    
    for idx, project in enumerate(projects, 1):
        print(f"{idx:2d}. | {project['id']} | {project['name']}")
    
    print("-" * 50)

    # Prompt for project selection
    while True:
        try:
            selection = input("\nEnter the number of the project you want to delete (or 'q' to quit): ")
            
            if selection.lower() == 'q':
                print("Operation cancelled.")
                return
            
            selection = int(selection)
            
            if 1 <= selection <= len(projects):
                selected_project = projects[selection - 1]
                print(f"\nSelected Project: {selected_project['name']} (ID: {selected_project['id']})")
                
                # Confirm deletion
                confirm = input("Are you sure you want to delete this project? (yes/no): ").lower()
                if confirm == 'yes':
                    if delete_entire_project(selected_project['id']):
                        print("Project deletion completed successfully.")
                    else:
                        print("Project deletion failed.")
                else:
                    print("Project deletion cancelled.")
                
                return
            else:
                print("Invalid selection. Please enter a valid number.")
        
        except ValueError:
            print("Please enter a valid number or 'q' to quit.")

if __name__ == "__main__":
    main()