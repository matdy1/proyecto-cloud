from openstack_sdk import password_authentication_with_scoped_authorization, token_authentication_with_scoped_authorization, create_server, get_server_console, create_project, assign_role_to_user_on_project, create_network, create_subnet, create_port
from dotenv import load_dotenv
import os

load_dotenv()
ACCESS_NODE_IP = os.getenv("ACCESS_NODE_IP")
KEYSTONE_PORT = os.getenv("KEYSTONE_PORT")
NOVA_PORT = os.getenv("NOVA_PORT")
NEUTRON_PORT = os.getenv("NEUTRON_PORT")
DOMAIN_ID = os.getenv("DOMAIN_ID")
ADMIN_PROJECT_ID = os.getenv("ADMIN_PROJECT_ID")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")
ADMIN_USER_PASSWORD = os.getenv("ADMIN_USER_PASSWORD")
COMPUTE_API_VERSION = os.getenv("COMPUTE_API_VERSION")
ADMIN_ROLE_ID = os.getenv("ADMIN_ROLE_ID")

KEYSTONE_ENDPOINT = 'http://' + ACCESS_NODE_IP + ':' + KEYSTONE_PORT + '/v3'
NOVA_ENDPOINT = 'http://' + ACCESS_NODE_IP + ':' + NOVA_PORT + '/v2.1'
NEUTRON_ENDPOINT = 'http://' + ACCESS_NODE_IP + ':' + NEUTRON_PORT + '/v2.0'

def get_admin_token():
    """

    INPUT:

    OUTPUT:
        admin_project_token = token with scope authorization over the admin project (clod_admin) | '' if something wrong
    
    """
    resp1 = password_authentication_with_scoped_authorization(KEYSTONE_ENDPOINT, ADMIN_USER_ID, ADMIN_USER_PASSWORD, DOMAIN_ID, ADMIN_PROJECT_ID)
    admin_project_token = ''
    if resp1.status_code == 201:
        admin_project_token = resp1.headers['X-Subject-Token']
    
    return admin_project_token

def get_token_for_project(project_id, admin_project_token):
    """

    INPUT:
        project_id = project identifier you need scoped authorization over
        admin_project_token = token with scope authorization over the admin project (cloud_admin)
    
    OUTPUT:
        token_for_project = token with scope authorization over the project identified by project_id | '' if something wrong
    
    """
    r = token_authentication_with_scoped_authorization(KEYSTONE_ENDPOINT, admin_project_token, DOMAIN_ID, project_id)
    token_for_project = ''
    if r.status_code == 201:
        token_for_project = r.headers['X-Subject-Token']
    
    return token_for_project

def create_os_instance(image_id, flavor_id, name, port_list, token_for_project):
    ports = [ { "port" : port } for port in port_list ]
    
    r = create_server(NOVA_ENDPOINT, token_for_project, name, flavor_id, image_id, ports)
    instance_info = {}
    if r.status_code == 202:
        instance_info = r.json()
        # Añade el nombre explícitamente para facilitar el acceso
        instance_info['instance_name'] = name
    
    return instance_info

def get_console_url(instance_id, admin_project_token):
    """

    INPUT:
        instance_id = identifier of instance whose console url you need
        admin_project_token = toker with scoped authorization over admin project (cloud_admin)
    
    OUTPUT:
        console_url =  console url of the intance identified by instance_id | '' if something wrong
    
    """
    r = get_server_console(NOVA_ENDPOINT, admin_project_token, instance_id, COMPUTE_API_VERSION)
    console_url = ''
    if r.status_code == 200:
        console_url = r.json()['remote_console']['url']
    
    return console_url

def create_os_project(admin_project_token, slice_name, slice_description = ''):
    
    r = create_project(KEYSTONE_ENDPOINT, admin_project_token, DOMAIN_ID, slice_name, slice_description)

    slice_id = ''
    if r.status_code == 201:
        slice_id = r.json()['project']['id']
    
    return slice_id
    
def assign_admin_role_over_os_project(admin_project_token, target_project_id):
    r = assign_role_to_user_on_project(KEYSTONE_ENDPOINT, admin_project_token, target_project_id, ADMIN_USER_ID, ADMIN_ROLE_ID)
    print(f"Role Assignment Response Status: {r.status_code}")
    print(f"Role Assignment Response Content: {r.text}")
    
    operation_status = 0
    if r.status_code == 204:
        operation_status = 1
    
    return operation_status

def create_os_network(target_project_token, network_name):
    r = create_network(NEUTRON_ENDPOINT, target_project_token, network_name)
    
    network_id = ''
    if r.status_code == 201:
        network_id = r.json()['network']['id']
    
    return network_id

def create_os_subnet(target_project_token, subnet_name, network_id):
    
    ip_version = '4'
    cidr = '10.0.39.96/28'

    r = create_subnet(NEUTRON_ENDPOINT, target_project_token, network_id, subnet_name, ip_version, cidr)
    
    subnet_id = ''
    if r.status_code == 201:
        subnet_id = r.json()['subnet']['id']
    
    return subnet_id

def create_os_port(target_project_token, port_name, network_id, target_project_id):

    r = create_port(NEUTRON_ENDPOINT, target_project_token, port_name, network_id, target_project_id)
    
    port_id = ''
    if r.status_code == 201:
        port_id = r.json()['port']['id']
    
    return port_id