import pathlib
import os
import subprocess
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import secrets
import string
from pathlib import Path
import itertools

loader = FileSystemLoader(searchpath="./")
environment = Environment(loader=loader)

VM_DIR = "/Users/qt/Virtual Machines.localized"

# collect nodes and group nodes master prefix is `m`, worker prefix is `w`
def create_inventories():
  master_nodes = {
    'primary': [], # first master node to be install with RKE
    'secondary': [], # other master nodes to be install with RKE
  }
  worker_nodes = {
    'compute': [],
    'memory': [],
    'disk': [],
    'generic': [],
  }
  other_nodes = {
    'load_balancers': []
  }
  api_servers = []
  
  host_file_records = []
  for filepath in pathlib.Path(VM_DIR).glob('*vmwarevm'):
    fn = filepath.absolute()
    ipaddr = subprocess.run(['vmrun', 'getGuestIPAddress', fn], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    node_name = Path(fn).stem
    node_prefix = node_name[0]
    
    # host file inventories
    host_file_records.append({
      'name': node_name, 
      'ipaddr': ipaddr
    })
    
    if node_prefix == 'm':
      # create primary and secondary node group
      if node_name == 'm1':
        master_nodes['primary'].append(ipaddr)
      else:
        master_nodes['secondary'].append(ipaddr)
      # configs for haproxy
      api_servers.append({
        'name': node_name,
        'ip_addr': ipaddr
      })
    elif node_prefix == 'l':
      other_nodes['load_balancers'].append(ipaddr)
    elif node_prefix == 'w':
      # also append to worker nodes (for later node labeling)
      worker_prefix = node_name.split('-')[1][0]
      if worker_prefix == 'm':
        worker_nodes['memory'].append(ipaddr)
      elif worker_prefix == 'c':
        worker_nodes['compute'].append(ipaddr)
      elif worker_prefix == 'd':
        worker_nodes['disk'].append(ipaddr)
      else:
        worker_nodes['generic'].append(ipaddr)
      
    print(node_name, ' ', ipaddr)
  
  cluster_nodes = {
    'masters': master_nodes,
    'workers': worker_nodes,
  }
  
  inventories = {}
  # import cluster nodes to inventory
  for group_name in cluster_nodes:
    for host_type in cluster_nodes[group_name]:
      ansible_key = host_type + '_' + group_name
      inventories[ansible_key] = {'hosts': {}}
      for ip_address in cluster_nodes[group_name][host_type]:
        inventories[ansible_key]['hosts'][ip_address] = ''
  # import other nodes
  for node_type in other_nodes:
    inventories[node_type] = {'hosts': {}}
    for ip_address in other_nodes[node_type]:
      inventories[node_type]['hosts'][ip_address] = ''
  
  with open('inventories.yaml', 'w') as outfile:
    yaml.dump(inventories, outfile, default_flow_style=False)
    
  # save cluster nodes to file for later use: update host file
  Path("configs/ansible_vars").mkdir(parents=True, exist_ok=True)
  with open('configs/ansible_vars/hosts.yaml', 'w') as outfile:
    yaml.dump({'hosts': host_file_records}, outfile, default_flow_style=False)
      
  return api_servers, cluster_nodes | other_nodes

def create_haproxy_config(api_servers):
  if not api_servers or len(api_servers) == 0:
    print('No API servers available')
  results_template = environment.get_template('templates/haproxy_config.j2')
  Path("configs/haproxy").mkdir(parents=True, exist_ok=True)
  with open('configs/haproxy/haproxy.cfg', mode="w", encoding="utf-8") as results:
      results.write(results_template.render(api_servers=api_servers) + '\n')
      
def get_cluster_token(prefix):
  cluster_token = ''
  Path("configs/cluster_tokens").mkdir(parents=True, exist_ok=True)
  token_file_name = f'configs/cluster_tokens/{prefix}'
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

def write_rke2_config(fn, **kwargs):
  tpl = environment.get_template('templates/rke2_config.j2')
  Path("configs/rke2_configs").mkdir(parents=True, exist_ok=True)
  with open(f'configs/rke2_configs/{fn}', mode="w") as file:
    file.write(tpl.render(kwargs) + '\n')

def create_rke_config(cluster_nodes):
  lb_ips = cluster_nodes['load_balancers']
  lb_ip = lb_ips[0]
  backends = list(itertools.chain(*cluster_nodes['masters'].values())) + lb_ips
  shared_token = get_cluster_token('shared')
  agent_token = get_cluster_token('agent')
  # create primary primary config
  write_rke2_config('primary_masters', backends=backends)
  # create secondary masters config
  write_rke2_config('secondary_masters', backends=backends, lb_ip=lb_ip)
  # create workers config
  for worker_type in cluster_nodes['workers']:
    write_rke2_config(f'{worker_type}_workers', worker_type=worker_type, lb_ip=lb_ip)
  # save lb ip in a file to be used for generate rke config later
  with open('configs/haproxy/ip_address', mode="w") as file:
    file.write(lb_ip)
      
      
api_servers, cluster_nodes = create_inventories()
create_haproxy_config(api_servers)
create_rke_config(cluster_nodes)
