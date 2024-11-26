import pathlib
import os
import subprocess
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import secrets
import string
from pathlib import Path

loader = FileSystemLoader(searchpath="./")
environment = Environment(loader=loader)

VM_DIR = "/Users/qt/Virtual Machines.localized"

Path("configs").mkdir(parents=True, exist_ok=True)

# collect nodes and group nodes master prefix is `m`, worker prefix is `w`
def create_inventories():
  cluster_nodes = {
    'load_balancer': [],
    'primary_master': [], # first master node to be install with RKE
    'secondary_masters': [], # other master nodes to be install with RKE
    'masters': [],
    'workers': [],
  }
  api_servers = []
  for filepath in pathlib.Path(VM_DIR).glob('*vmwarevm'):
    fn = filepath.absolute()
    ipaddr = subprocess.run(['vmrun', 'getGuestIPAddress', fn], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    node_name = Path(fn).stem
    node_prefix = node_name[0]
    
    role = 'workers'
    if node_prefix == 'm':
      role = 'masters'
      api_servers.append({
        'name': node_name,
        'ip_addr': ipaddr
      })
    elif node_prefix == 'l':
      role = 'load_balancer'
    else:
      role = 'workers'
      
    cluster_nodes[role].append(ipaddr)
    print(node_name, ' ', ipaddr)
    if node_prefix == 'm':
      if len(cluster_nodes['primary_master']) == 0 and '1' in node_name:
        cluster_nodes['primary_master'].append(ipaddr)
      else:
        cluster_nodes['secondary_masters'].append(ipaddr)
    
  inventories = {}
  for key in cluster_nodes:
    inventories[key] = {'hosts': {}}
    for ip_address in cluster_nodes[key]:
      inventories[key]['hosts'][ip_address] = ''

  with open('inventories.yaml', 'w') as outfile:
    yaml.dump(inventories, outfile, default_flow_style=False)
  return api_servers, cluster_nodes

def create_haproxy_config(api_servers):
  if not api_servers or len(api_servers) == 0:
    print('No API servers available')
  results_template = environment.get_template('templates/haproxy_config.j2')
  with open('configs/haproxy_config', mode="w", encoding="utf-8") as results:
      results.write(results_template.render(api_servers=api_servers) + '\n')
      
def get_cluster_token():
  cluster_token = ''
  token_file_name = 'cluster_token'
  if os.path.isfile(token_file_name):
    print(f'Token file "{token_file_name}" found in path, using it as cluster token')
    token_file = open(token_file_name, 'r')
    cluster_token = token_file.read().strip()
    token_file.close()
  else:
    print(f'Token file "{token_file_name}" does not found in path, generate random cluster token')
    alphabet = string.ascii_letters + string.digits
    cluster_token = ''.join(secrets.choice(alphabet) for i in range(20))  # for a 20-character password
    # save in to token file
    token_file = open(token_file_name, 'w')
    token_file.write(cluster_token)
    token_file.close()
  return cluster_token

def create_rke_config(api_servers):
  results_template = environment.get_template('templates/rke2_config.j2')
  backends = cluster_nodes['primary_master'] + cluster_nodes['secondary_masters'] + cluster_nodes['load_balancer']
  token = get_cluster_token()
  lb_ip = cluster_nodes['load_balancer'][0]
  # create primary primary config
  with open('configs/rke2_config_master_pri', mode="w") as file:
    file.write(results_template.render(backends=backends, token=token,) + '\n')
  # create secondary masters config
  with open('configs/rke2_config_master_sec', mode="w") as file:
    file.write(results_template.render(backends=backends, token=token, lb_ip=lb_ip) + '\n')
  # create workers config
  with open('configs/rke2_config_worker', mode="w") as file:
    file.write(results_template.render(token=token, lb_ip=lb_ip) + '\n')
  # save lb ip in a file to be used for generate rke config later
  with open('configs/loadbalancer_ip', mode="w") as file:
    file.write(lb_ip)
      
api_servers, cluster_nodes = create_inventories()
create_haproxy_config(api_servers)
create_rke_config(cluster_nodes)