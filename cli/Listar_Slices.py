import sys
from openstack_sf import get_admin_token

from openstack_sdk import (
    list_projects,
    list_networks,
    list_subnets,
    list_ports,
    list_servers  # Usaremos list_servers en lugar de list_instances
)
from json import dumps as jdumps

import os
from dotenv import load_dotenv

load_dotenv()

KEYSTONE_ENDPOINT = f'http://{os.getenv("ACCESS_NODE_IP")}:{os.getenv("KEYSTONE_PORT")}/v3'
NOVA_ENDPOINT = f'http://{os.getenv("ACCESS_NODE_IP")}:{os.getenv("NOVA_PORT")}/v2.1'
NEUTRON_ENDPOINT = f'http://{os.getenv("ACCESS_NODE_IP")}:{os.getenv("NEUTRON_PORT")}/v2.0'

def list_topologies():
    """
    List all OpenStack projects (topologies) and allow the user to select one for details.
    """
    try:
        # Step 1: Get admin token
        admin_token = get_admin_token()
        if not admin_token:
            print("ERROR: Failed to obtain admin token")
            return

        # Step 2: List all projects
        projects_response = list_projects(KEYSTONE_ENDPOINT, admin_token)
        if projects_response.status_code != 200:
            print("Failed to retrieve projects")
            return

        projects = projects_response.json().get('projects', [])

        if not projects:
            print("No projects found.")
            return

        print("Available Topologies:")
        for idx, project in enumerate(projects, start=1):
            print(f"{idx}. {project['name']} (ID: {project['id']})")

        # Step 3: Select a project
        selection = int(input("\nSelect a topology by number: ")) - 1
        if selection < 0 or selection >= len(projects):
            print("Invalid selection.")
            return

        selected_project = projects[selection]
        project_id = selected_project['id']
        print(f"\nSelected Topology: {selected_project['name']} (ID: {project_id})")

        # Step 4: Get details of the selected project
        networks_response = list_networks(NEUTRON_ENDPOINT, admin_token, project_id)
        subnets_response = list_subnets(NEUTRON_ENDPOINT, admin_token, project_id)
        ports_response = list_ports(NEUTRON_ENDPOINT, admin_token, project_id)
        servers_response = list_servers(NOVA_ENDPOINT, admin_token, project_id)

        networks = networks_response.json().get('networks', []) if networks_response.status_code == 200 else []
        subnets = subnets_response.json().get('subnets', []) if subnets_response.status_code == 200 else []
        ports = ports_response.json().get('ports', []) if ports_response.status_code == 200 else []
        servers = servers_response.json().get('servers', []) if servers_response.status_code == 200 else []

        print("\nNetworks:")
        for network in networks:
            print(f"  - {network['name']} (ID: {network['id']})")

        print("\nSubnets:")
        for subnet in subnets:
            print(f"  - {subnet['name']} (ID: {subnet['id']}, Network: {subnet['network_id']})")

        print("\nPorts:")
        for port in ports:
            print(f"  - {port['name']} (ID: {port['id']}, Network: {port['network_id']})")

        print("\nServers:")
        for server in servers:
            print(f"  - {server['name']} (ID: {server['id']})")

        # Optional: Generate graphical representation
        generate_topology_graph(selected_project['name'], networks, subnets, ports, servers)

    except Exception as e:
        print(f"Error listing topologies: {e}")

def generate_topology_graph(topology_name, networks, subnets, ports, servers):
    """
    Generate a graphical representation of the topology with specific styles for servers, networks, subnets, and ports.
    """
    try:
        import networkx as nx
        import matplotlib.pyplot as plt

        graph = nx.DiGraph()

        # Add nodes and edges for networks
        for network in networks:
            graph.add_node(network['id'], label=network['name'], shape='square', color='blue')

        # Add nodes and edges for subnets
        for subnet in subnets:
            graph.add_node(subnet['id'], label=subnet['name'], shape='triangle', color='green')
            graph.add_edge(subnet['network_id'], subnet['id'], label='Subnet of')

        # Add nodes and edges for ports
        for port in ports:
            graph.add_node(port['id'], label=port['name'], shape='hexagon', color='orange')
            graph.add_edge(port['network_id'], port['id'], label='Port of')

        # Add nodes and edges for servers
        for server in servers:
            graph.add_node(server['id'], label=server['name'], shape='circle', color='red')
            for port in ports:
                if port['device_id'] == server['id']:
                    graph.add_edge(port['id'], server['id'], label='Connected to')

        # Generate positions for the graph
        pos = nx.spring_layout(graph)

        # Draw nodes with different styles
        node_shapes = {'circle': [], 'square': [], 'triangle': [], 'hexagon': []}
        for node, attr in graph.nodes(data=True):
            node_shapes[attr['shape']].append(node)

        # Draw each shape separately
        for shape, nodes in node_shapes.items():
            if nodes:
                nx.draw_networkx_nodes(
                    graph, pos, nodelist=nodes,
                    node_color=[graph.nodes[n]['color'] for n in nodes],
                    node_shape=_get_node_shape(shape),
                    label=f"{shape.capitalize()}s"
                )

        # Draw edges
        nx.draw_networkx_edges(graph, pos)
        nx.draw_networkx_labels(graph, pos, labels=nx.get_node_attributes(graph, 'label'))
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=nx.get_edge_attributes(graph, 'label'))

        plt.title(f"Topology: {topology_name}")
        plt.legend()
        plt.show()

    except ImportError:
        print("Graphical representation requires 'networkx' and 'matplotlib' libraries.")
    except Exception as e:
        print(f"Error generating topology graph: {e}")

def _get_node_shape(shape):
    """
    Map custom shape names to matplotlib marker symbols.
    """
    shape_map = {
        'circle': 'o',
        'square': 's',
        'triangle': '^',
        'hexagon': 'h'
    }
    return shape_map.get(shape, 'o')  # Default to 'circle' if shape is not defined


if __name__ == "__main__":
    list_topologies()
