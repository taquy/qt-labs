import pathlib
import os
import subprocess
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import secrets
import string
import itertools

loader = FileSystemLoader(searchpath="./")
environment = Environment(loader=loader)

def create_inventories():
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
  Path("configs/rke2/tokens").mkdir(parents=True, exist_ok=True)
  token_file_name = f'configs/rke2/tokens/{prefix}'
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
  Path("configs/rke2/configs").mkdir(parents=True, exist_ok=True)
  with open(f'configs/rke2/configs/{fn}', mode="w") as file:
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
