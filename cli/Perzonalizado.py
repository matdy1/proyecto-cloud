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

def create_topologies(project_token, project_id, linear_nodes, ring_nodes, image_id, flavor_id):
    topology_resources = {
        'linear': {
            'networks': [],
            'subnets': [],
            'ports': [],
            'instances': []
        },
        'ring': {
            'networks': [],
            'subnets': [],
            'ports': [],
            'instances': []
        }
    }

    try:
        # Create Linear Topology
        print("Creating Linear Topology...")
        for link_num in range(1, linear_nodes):
            network_name = f"link_lineal_{link_num}"
            network_id = create_os_network(project_token, network_name)
            topology_resources['linear']['networks'].append(network_id)

            subnet_name = f"subnet_lineal_{link_num}"
            subnet_id = create_os_subnet(project_token, subnet_name, network_id)
            topology_resources['linear']['subnets'].append(subnet_id)

            port1_id = create_os_port(project_token, f"port_1_lineal_{link_num}", network_id, project_id)
            port2_id = create_os_port(project_token, f"port_2_lineal_{link_num}", network_id, project_id)
            topology_resources['linear']['ports'].extend([port1_id, port2_id])

        for node_num in range(1, linear_nodes + 1):
            instance_name = f"linear_node_{node_num}"
            ports = []

            if node_num == 1:
                ports = [topology_resources['linear']['ports'][0]]
            elif node_num == linear_nodes:
                ports = [topology_resources['linear']['ports'][-1]]
            else:
                ports = [
                    topology_resources['linear']['ports'][(node_num - 2) * 2 + 1],
                    topology_resources['linear']['ports'][(node_num - 1) * 2]
                ]

            instance_info = create_os_instance(image_id, flavor_id, instance_name, ports, project_token)
            topology_resources['linear']['instances'].append(instance_info)

        # Create Ring Topology
        print("Creating Ring Topology...")
        for node_num in range(1, ring_nodes + 1):
            network_name = f"link_ring_{node_num}"
            network_id = create_os_network(project_token, network_name)
            topology_resources['ring']['networks'].append(network_id)

            subnet_name = f"subnet_ring_{node_num}"
            subnet_id = create_os_subnet(project_token, subnet_name, network_id)
            topology_resources['ring']['subnets'].append(subnet_id)

            port1_id = create_os_port(project_token, f"port_1_ring_{node_num}", network_id, project_id)
            port2_id = create_os_port(project_token, f"port_2_ring_{node_num}", network_id, project_id)
            topology_resources['ring']['ports'].extend([port1_id, port2_id])

        for node_num in range(1, ring_nodes + 1):
            instance_name = f"ring_node_{node_num}"
            prev_port_index = 2 * ((node_num - 2) % ring_nodes) + 1
            next_port_index = 2 * ((node_num - 1) % ring_nodes)
            ports = [
                topology_resources['ring']['ports'][prev_port_index],
                topology_resources['ring']['ports'][next_port_index]
            ]

            instance_info = create_os_instance(image_id, flavor_id, instance_name, ports, project_token)
            topology_resources['ring']['instances'].append(instance_info)

        return topology_resources

    except Exception as e:
        print(f"Error creating topologies: {e}")
        return None

def main():
    print("Welcome to the Topology Creator")

    # Step 1: Gather input from user
    topology_name = input("Enter the topology name: ")
    linear_nodes = int(input("Enter the number of nodes for the linear topology: "))
    ring_nodes = int(input("Enter the number of nodes for the ring topology: "))

    # Step 2: Get admin token and create project
    admin_token = get_admin_token()
    if not admin_token:
        print("ERROR: Failed to obtain admin token")
        sys.exit(1)

    project_name = f"{topology_name}_project"
    project_id = create_os_project(admin_token, project_name)
    assign_admin_role_over_os_project(admin_token, project_id)
    project_token = get_token_for_project(project_id, admin_token)

    # Step 3: Create topologies
    resources = create_topologies(project_token, project_id, linear_nodes, ring_nodes, DEFAULT_IMAGE_ID, DEFAULT_FLAVOR_ID)

    if not resources:
        print("Failed to create topologies")
        sys.exit(1)

    # Step 4: Connect nodes
    print("\nSelect a node from the Linear Topology:")
    for i, instance in enumerate(resources['linear']['instances'], start=1):
        print(f"{i}. {instance['name']}")
    linear_choice = int(input("Choose a node: ")) - 1

    print("\nSelect a node from the Ring Topology:")
    for i, instance in enumerate(resources['ring']['instances'], start=1):
        print(f"{i}. {instance['name']}")
    ring_choice = int(input("Choose a node: ")) - 1

    linear_node = resources['linear']['instances'][linear_choice]
    ring_node = resources['ring']['instances'][ring_choice]

    print(f"Connecting {linear_node['name']} to {ring_node['name']}...")

    try:
        # Create a network and ports to connect the selected nodes
        connection_network = create_os_network(project_token, "connection_network")
        connection_subnet = create_os_subnet(project_token, "connection_subnet", connection_network)

        linear_port = create_os_port(project_token, "linear_connection_port", connection_network, project_id)
        ring_port = create_os_port(project_token, "ring_connection_port", connection_network, project_id)

        create_os_instance(DEFAULT_IMAGE_ID, DEFAULT_FLAVOR_ID, linear_node['name'], [linear_port], project_token)
        create_os_instance(DEFAULT_IMAGE_ID, DEFAULT_FLAVOR_ID, ring_node['name'], [ring_port], project_token)

        print("Connection established successfully!")

    except Exception as e:
        print(f"Failed to connect nodes: {e}")

if __name__ == "__main__":
    main()
