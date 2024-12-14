import sys
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

# Default Image and Flavor IDs
DEFAULT_IMAGE_ID = '4f0d4d09-d6bc-4a65-8ce2-1a181fa3e458'
DEFAULT_FLAVOR_ID = 'cdd2dc7f-b00b-483d-a104-4cea575c9b1b'

def create_ring_topology(topology_name, num_nodes, image_id=DEFAULT_IMAGE_ID, flavor_id=DEFAULT_FLAVOR_ID):
    """
    Create an OpenStack ring topology with the specified number of nodes.

    :param topology_name: Name of the topology
    :param num_nodes: Number of nodes in the ring
    :param image_id: OpenStack image ID to use for instances
    :param flavor_id: OpenStack flavor ID to use for instances
    :return: Dictionary containing project and resource IDs
    """
    admin_project_token = get_admin_token()
    if not admin_project_token:
        print("ERROR: Failed to obtain admin token")
        return None

    topology_resources = {
        'project_id': None,
        'networks': [],
        'subnets': [],
        'ports': [],
        'instances': []
    }

    try:
        # Step 1: Create Project
        project_name = f"{topology_name}_project"
        project_id = create_os_project(admin_project_token, project_name)
        topology_resources['project_id'] = project_id
        print(f"Created project: {project_name} (ID: {project_id})")

        # Step 2: Assign admin role to the project
        assign_admin_role_over_os_project(admin_project_token, project_id)
        print("Admin role assigned successfully")

        # Step 3: Get project token
        project_token = get_token_for_project(project_id, admin_project_token)
        if not project_token:
            print("ERROR: Failed to get project token")
            return None

        # Step 4: Create Networks, Subnets, and Ports
        for node_num in range(1, num_nodes + 1):
            # Create Network
            network_name = f"link_anillo_{node_num}_{topology_name}"
            network_id = create_os_network(project_token, network_name)
            topology_resources['networks'].append(network_id)
            print(f"Created network: {network_name} (ID: {network_id})")

            # Create Subnet
            subnet_name = f"subnet_link_anillo_{node_num}_{topology_name}"
            subnet_id = create_os_subnet(project_token, subnet_name, network_id)
            topology_resources['subnets'].append(subnet_id)
            print(f"Created subnet: {subnet_name} (ID: {subnet_id})")

            # Create Ports
            port1_name = f"port_1_link_{node_num}"
            port2_name = f"port_2_link_{node_num}"

            port1_id = create_os_port(project_token, port1_name, network_id, project_id)
            port2_id = create_os_port(project_token, port2_name, network_id, project_id)

            topology_resources['ports'].extend([port1_id, port2_id])
            print(f"Created ports for link {node_num}: {port1_name}, {port2_name}")

        # Step 5: Create Instances and Connect Them in a Ring
        for node_num in range(1, num_nodes + 1):
            instance_name = f"{topology_name}_node_{node_num}"

            # Determine ports to connect
            try:
                # Port connecting to the previous node
                prev_port_index = 2 * ((node_num - 2) % num_nodes) + 1  # Previous node's second port
                # Port connecting to the next node
                next_port_index = 2 * ((node_num - 1) % num_nodes)      # Current node's first port

                prev_port = topology_resources['ports'][prev_port_index]
                next_port = topology_resources['ports'][next_port_index]

                print(f"\nCreating instance {instance_name} with ports:")
                print(f"Port 1 (to previous): {prev_port}")
                print(f"Port 2 (to next): {next_port}")

                # Create instance
                instance_info = create_os_instance(
                    image_id,
                    flavor_id,
                    instance_name,
                    [prev_port, next_port],
                    project_token
                )

                topology_resources['instances'].append(instance_info)
                print(f"Created instance: {instance_name}")

            except Exception as e:
                print(f"Failed to create instance {instance_name}: {e}")
                continue  # Proceed with the next instance


        return topology_resources

    except Exception as e:
        print(f"Error creating topology: {e}")
        return None
    
def main():
    # Validate arguments
    if len(sys.argv) < 3:
        print("Usage: python script.py ring <num_nodes> [image_id] [flavor_id]")
        sys.exit(1)

    topology_name = sys.argv[1]
    num_nodes = int(sys.argv[2])

    image_id = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_IMAGE_ID
    flavor_id = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_FLAVOR_ID

    result = create_ring_topology(topology_name, num_nodes, image_id, flavor_id)

    if result:
        print("\nTopology Creation Summary:")
        print(jdumps(result, indent=2))

if __name__ == "__main__":
    main()