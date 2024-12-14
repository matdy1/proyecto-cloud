import sys
import mysql.connector
from openstack_sf import (
    get_admin_token, 
    get_token_for_project, 
    create_os_project, 
    assign_admin_role_over_os_project, 
    create_os_network, 
    create_os_subnet, 
    create_os_port, 
    create_os_instance
)
from json import dumps as jdumps

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'proyectoCloud'
}

# Default Image and Flavor IDs
DEFAULT_IMAGE_ID = '4f0d4d09-d6bc-4a65-8ce2-1a181fa3e458'
DEFAULT_FLAVOR_ID = 'cdd2dc7f-b00b-483d-a104-4cea575c9b1b'

def save_project_to_db(project_id, topology_name, selected_user):
    """
    Guarda el ID del proyecto creado y el usuario seleccionado en la base de datos.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Insertar en la tabla "topologias"
        query = """
            INSERT INTO slices (idProyecto, usuario) 
            VALUES (%s, %s)
        """
        cursor.execute(query, (project_id, selected_user))
        connection.commit()
        print(f"Project ID {project_id} guardado en la base de datos con el usuario {selected_user}")
    
    except mysql.connector.Error as e:
        print(f"Error al guardar en la base de datos: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_linear_topology(topology_name, num_nodes, image_id, flavor_id, selected_user):
    """
    Create an OpenStack linear topology with specified number of nodes.
    """
    topology_resources = {
        'project_id': None,
        'networks': [],
        'subnets': [],
        'ports': [],
        'instances': []
    }
    
    try:
        # Step 1: Get admin token
        admin_project_token = get_admin_token()
        if not admin_project_token:
            raise Exception("Failed to obtain admin token")
        
        # Step 2: Create Project
        project_name = f"{topology_name}_project"
        project_id = create_os_project(admin_project_token, project_name)
        topology_resources['project_id'] = project_id
        print(f"Created project: {project_name} (ID: {project_id})")
        
        # Guardar el proyecto en la base de datos
        save_project_to_db(project_id, topology_name, selected_user)
        
        # Step 3: Assign admin role to the project
        assign_admin_role_over_os_project(admin_project_token, project_id)
        print("Admin role assigned successfully")
        
        # Get project token
        project_token = get_token_for_project(project_id, admin_project_token)
        
        # Step 4: Create Linear Networks and Ports
        for link_num in range(1, num_nodes):
            network_name = f"link_lineal_{link_num}_{topology_name}"
            network_id = create_os_network(project_token, network_name)
            topology_resources['networks'].append(network_id)
            print(f"Created network: {network_name} (ID: {network_id})")
            
            subnet_name = f"subnet_link_lineal_{link_num}_{topology_name}"
            subnet_id = create_os_subnet(project_token, subnet_name, network_id)
            topology_resources['subnets'].append(subnet_id)
            print(f"Created subnet: {subnet_name} (ID: {subnet_id})")
            
            port1_id = create_os_port(project_token, f"port_1_link_{link_num}", network_id, project_id)
            port2_id = create_os_port(project_token, f"port_2_link_{link_num}", network_id, project_id)
            topology_resources['ports'].extend([port1_id, port2_id])
            print(f"Created ports for link {link_num}: port_1_link_{link_num}, port_2_link_{link_num}")
        
        # Step 5: Create Linear Topology Instances
        for node_num in range(1, num_nodes + 1):
            instance_name = f"{topology_name}_node_{node_num}"
            
            if node_num == 1:
                instance_ports = [topology_resources['ports'][0]]
            elif node_num == num_nodes:
                instance_ports = [topology_resources['ports'][-1]]
            else:
                instance_ports = [
                    topology_resources['ports'][(node_num - 2) * 2 + 1],  
                    topology_resources['ports'][(node_num - 1) * 2]
                ]
            
            instance_info = create_os_instance(
                image_id, 
                flavor_id, 
                instance_name, 
                instance_ports, 
                project_token
            )
            topology_resources['instances'].append(instance_info)
            print(f"Created instance: {instance_name}")
        
        return topology_resources
    
    except Exception as e:
        print(f"Error creating topology: {e}")
        return None

def main():
    # Validar argumentos
    if len(sys.argv) < 6:
        print("Uso: python Lineal_OP.py <topology_name> <num_nodes> <image_id> <flavor_id> <selected_user>")
        sys.exit(1)
    
    topology_name = sys.argv[1]
    num_nodes = int(sys.argv[2])
    image_id = sys.argv[3]
    flavor_id = sys.argv[4]
    selected_user = sys.argv[5]
    
    # Crear topología
    result = create_linear_topology(topology_name, num_nodes, image_id, flavor_id, selected_user)
    
    if result:
        print("\nResumen de creación de topología:")
        print(jdumps(result, indent=2))

if __name__ == "__main__":
    main()
