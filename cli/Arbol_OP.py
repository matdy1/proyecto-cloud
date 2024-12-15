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

def create_tree_topology(topology_name, levels, nodes_per_level, image_id=DEFAULT_IMAGE_ID, flavor_id=DEFAULT_FLAVOR_ID):
    """
    Create an OpenStack tree topology with the specified levels and nodes per level.

    :param topology_name: Name of the topology
    :param levels: Number of levels in the tree
    :param nodes_per_level: Number of nodes per level (except root level which has 1 node)
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
        previous_level_ports = []

        for level in range(1, levels + 1):
            current_level_ports = []
            nodes_in_level = 1 if level == 1 else nodes_per_level

            for node in range(1, nodes_in_level + 1):
                # Create Instance
                instance_name = f"{topology_name}_level_{level}_node_{node}"
                instance_ports = []

                if level > 1:
                    # Connect to parent node
                    parent_index = (node - 1) // nodes_per_level
                    parent_port = previous_level_ports[parent_index]

                    # Create Network for connection
                    network_name = f"link_tree_level_{level}_node_{node}_{topology_name}"
                    network_id = create_os_network(project_token, network_name)
                    topology_resources['networks'].append(network_id)
                    print(f"Created network: {network_name} (ID: {network_id})")

                    # Create Subnet
                    subnet_name = f"subnet_tree_level_{level}_node_{node}_{topology_name}"
                    subnet_id = create_os_subnet(project_token, subnet_name, network_id)
                    topology_resources['subnets'].append(subnet_id)
                    print(f"Created subnet: {subnet_name} (ID: {subnet_id})")

                    # Create Port for parent connection
                    parent_connection_port_name = f"port_parent_tree_level_{level}_node_{node}"
                    parent_connection_port_id = create_os_port(project_token, parent_connection_port_name, network_id, project_id)
                    topology_resources['ports'].append(parent_connection_port_id)

                    # Connect parent port to this instance
                    instance_ports.append(parent_connection_port_id)

                    # Create Port for this node
                    port_name = f"port_tree_level_{level}_node_{node}"
                    port_id = create_os_port(project_token, port_name, network_id, project_id)
                    topology_resources['ports'].append(port_id)
                    current_level_ports.append(port_id)

                    # Connect this port to the instance
                    instance_ports.append(port_id)

                print(f"\nCreating instance {instance_name} with ports: {instance_ports}")

                # Create instance
                instance_info = create_os_instance(
                    image_id,
                    flavor_id,
                    instance_name,
                    instance_ports,
                    project_token
                )

                topology_resources['instances'].append(instance_info)
                print(f"Created instance: {instance_name}")

            previous_level_ports = current_level_ports

        return topology_resources

    except Exception as e:
        print(f"Error creating topology: {e}")
        return None

def main():
    # Validate arguments
    if len(sys.argv) < 4:
        print("Usage: python script.py tree <levels> <nodes_per_level> [image_id] [flavor_id]")
        sys.exit(1)

    topology_name = sys.argv[1]
    levels = int(sys.argv[2])
    nodes_per_level = int(sys.argv[3])

    image_id = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_IMAGE_ID
    flavor_id = sys.argv[5] if len(sys.argv) > 5 else DEFAULT_FLAVOR_ID

    result = create_tree_topology(topology_name, levels, nodes_per_level, image_id, flavor_id)

    if result:
        print("\nTopology Creation Summary:")
        print(jdumps(result, indent=2))

if __name__ == "__main__":
    main()
