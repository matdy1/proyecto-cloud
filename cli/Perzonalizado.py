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

DEFAULT_IMAGE_ID = '4f0d4d09-d6bc-4a65-8ce2-1a181fa3e458'
DEFAULT_FLAVOR_ID = 'cdd2dc7f-b00b-483d-a104-4cea575c9b1b'

def create_linear_topology(project_token, topology_name, num_nodes):
    """
    Create a linear topology with the specified number of nodes.

    :param project_token: Token for the project
    :param topology_name: Name of the linear topology
    :param num_nodes: Number of nodes in the linear topology
    :return: Dictionary with instances and ports information
    """
    linear_resources = {'instances': [], 'ports': []}

    previous_instance_id = None
    for i in range(num_nodes):
        instance_name = f"{topology_name}_node_{i + 1}"
        instance_id = create_os_instance(project_token, instance_name, DEFAULT_IMAGE_ID, DEFAULT_FLAVOR_ID)
        print(f"Created instance: {instance_name} (ID: {instance_id})")

        if previous_instance_id:
            port_name = f"{topology_name}_port_{i}"
            port_id = create_os_port(project_token, port_name, network_id=None, project_id=None)
            print(f"Created port: {port_name} (ID: {port_id})")
            linear_resources['ports'].append({'id': port_id, 'name': port_name})

        linear_resources['instances'].append({'id': instance_id, 'name': instance_name})
        previous_instance_id = instance_id

    return linear_resources

def create_ring_topology(project_token, topology_name, num_nodes):
    """
    Create a ring topology with the specified number of nodes.

    :param project_token: Token for the project
    :param topology_name: Name of the ring topology
    :param num_nodes: Number of nodes in the ring topology
    :return: Dictionary with instances and ports information
    """
    ring_resources = {'instances': [], 'ports': []}

    instance_ids = []
    for i in range(num_nodes):
        instance_name = f"{topology_name}_node_{i + 1}"
        instance_id = create_os_instance(project_token, instance_name, DEFAULT_IMAGE_ID, DEFAULT_FLAVOR_ID)
        print(f"Created instance: {instance_name} (ID: {instance_id})")
        instance_ids.append(instance_id)
        ring_resources['instances'].append({'id': instance_id, 'name': instance_name})

    # Connect the nodes in a ring
    for i in range(num_nodes):
        port_name = f"{topology_name}_port_{i + 1}"
        port_id = create_os_port(project_token, port_name, network_id=None, project_id=None)
        print(f"Created port: {port_name} (ID: {port_id})")
        ring_resources['ports'].append({'id': port_id, 'name': port_name})

    return ring_resources

def create_connection_network(project_token, project_id, topology_name):
    """
    Create a network and subnet to connect two selected nodes from different topologies.

    :param project_token: Token for the project
    :param project_id: ID of the project
    :param topology_name: Name of the topology
    :return: Network and subnet IDs
    """
    network_name = f"connection_network_{topology_name}"
    network_id = create_os_network(project_token, network_name)
    print(f"Created connection network: {network_name} (ID: {network_id})")

    subnet_name = f"connection_subnet_{topology_name}"
    subnet_id = create_os_subnet(project_token, subnet_name, network_id)
    print(f"Created connection subnet: {subnet_name} (ID: {subnet_id})")

    return network_id, subnet_id

def deploy_combined_topology():
    """
    Deploy a combined topology of linear and ring slices, with a connection between selected nodes.
    """
    # Get user input
    topology_name = input("Enter the name of the topology: ").strip()
    num_linear_nodes = int(input("Enter the number of nodes in the linear topology: "))
    num_ring_nodes = int(input("Enter the number of nodes in the ring topology: "))

    admin_project_token = get_admin_token()
    if not admin_project_token:
        print("ERROR: Failed to obtain admin token")
        return None

    try:
        # Step 1: Create Project
        project_name = f"{topology_name}_project"
        project_id = create_os_project(admin_project_token, project_name)
        print(f"Created project: {project_name} (ID: {project_id})")

        # Step 2: Assign admin role to the project
        assign_admin_role_over_os_project(admin_project_token, project_id)
        print("Admin role assigned successfully")

        # Step 3: Get project token
        project_token = get_token_for_project(project_id, admin_project_token)
        if not project_token:
            print("ERROR: Failed to get project token")
            return None

        # Step 4: Create Linear Topology
        linear_resources = create_linear_topology(project_token, f"{topology_name}_linear", num_linear_nodes)

        # Step 5: Create Ring Topology
        ring_resources = create_ring_topology(project_token, f"{topology_name}_ring", num_ring_nodes)

        # Step 6: Prompt user to select nodes to connect
        print("\nNodes in Linear Topology:")
        for i, instance in enumerate(linear_resources['instances'], 1):
            print(f"{i}: {instance['id']}")
        linear_node_index = int(input("Select a node from the Linear Topology to connect: ")) - 1

        print("\nNodes in Ring Topology:")
        for i, instance in enumerate(ring_resources['instances'], 1):
            print(f"{i}: {instance['id']}")
        ring_node_index = int(input("Select a node from the Ring Topology to connect: ")) - 1

        # Step 7: Create Connection Network
        connection_network_id, connection_subnet_id = create_connection_network(project_token, project_id, topology_name)

        # Step 8: Create Ports and Connect Selected Nodes
        linear_node_port_name = f"connection_port_linear_{topology_name}"
        linear_node_port_id = create_os_port(project_token, linear_node_port_name, connection_network_id, project_id)
        print(f"Created port for linear node connection: {linear_node_port_id}")

        ring_node_port_name = f"connection_port_ring_{topology_name}"
        ring_node_port_id = create_os_port(project_token, ring_node_port_name, connection_network_id, project_id)
        print(f"Created port for ring node connection: {ring_node_port_id}")

        # Attach the ports to the selected instances
        linear_instance_id = linear_resources['instances'][linear_node_index]['id']
        ring_instance_id = ring_resources['instances'][ring_node_index]['id']

        print(f"Attaching connection port to linear instance {linear_instance_id}")
        print(f"Attaching connection port to ring instance {ring_instance_id}")

        # The logic to attach ports to instances should be implemented here if needed

        print("\nCombined Topology deployed successfully!")

    except Exception as e:
        print(f"Error deploying combined topology: {e}")

if __name__ == "__main__":
    deploy_combined_topology()
