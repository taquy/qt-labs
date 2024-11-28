import pathlib
import os
import subprocess
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import secrets
import string
import itertools
import re

loader = FileSystemLoader(searchpath="./")
environment = Environment(loader=loader)

class AnsibleInventoryService:
  lb_virtual_ip = ''
  lb_primary_nic = ''
  load_balancers = []
  cluster_nodes = {}
  other_nodes = {}
  api_servers = []
  
  def __init__(self):
    self._load_vm_lists()
    
  def _load_vm_lists(self):
    with open('configs/vm_lists.yaml', mode="r") as file:
      vm_lists = yaml.load(file, Loader=yaml.FullLoader)
      hosts = vm_lists.get('hosts')
      self.cluster_nodes = hosts.get('cluster_nodes')
      self.other_nodes = hosts.get('other_nodes')
      self.api_servers = hosts.get('api_servers')
      self.load_balancers = hosts.get('load_balancers')
      self._save_hosts_file_variables(hosts.get('hosts_file_records'))
    with open('configs/haproxy/lb_virtual_ip', mode="r") as file:
      self.lb_virtual_ip = file.read()
    with open('configs/haproxy/lb_primary_nic', mode="r") as file:
      self.lb_primary_nic = file.read()

  def create_inventories(self):
    inventories = {}
    # import cluster nodes to inventory
    for group_name in self.cluster_nodes:
      for host_type in self.cluster_nodes[group_name]:
        ansible_key = host_type + '_' + group_name
        inventories[ansible_key] = {'hosts': {}}
        for ip_address in self.cluster_nodes[group_name][host_type]:
          inventories[ansible_key]['hosts'][ip_address] = ''
    # import other nodes
    for node_type in self.other_nodes:
      inventories[node_type] = {'hosts': {}}
      for ip_address in self.other_nodes[node_type]:
        inventories[node_type]['hosts'][ip_address] = ''
    with open('inventories.yaml', 'w') as outfile:
      yaml.dump(inventories, outfile, default_flow_style=False)
      
  def _save_hosts_file_variables(self, hosts_file_records):
    # save cluster nodes to file for later use: update host file
    with open('configs/hosts.yaml', 'w') as outfile:
      yaml.dump({
        'hosts': hosts_file_records
      }, outfile, default_flow_style=False)

  def create_haproxy_config(self):
    if not self.api_servers or len(self.api_servers) == 0:
      print('No API servers available')
    lb_ips = self.other_nodes['load_balancers']
    password = self._generate_password(10)
    tpl = environment.get_template('templates/keepalived.j2')
    default_priority = 101
    for lb in self.load_balancers:
      current_host = lb.get('name')
      host_index = int(''.join(filter(str.isdigit, current_host)))
      priority = default_priority - host_index
      is_master = host_index == 1
      current_ip = lb.get('ip_addr')
      peer_ips = lb_ips.copy()
      peer_ips.remove(current_ip)
      with open(f'configs/haproxy/keepalived_{current_host}.conf', mode='w', encoding='utf-8') as results:
          results.write(tpl.render(
            current_host=current_host,
            nic=self.lb_primary_nic,
            is_master=is_master,
            password=password,
            virtual_ip=self.lb_virtual_ip,
            peer_ips=peer_ips,
            priority=priority
          ) + '\n')
    
  def _generate_password(self, pwd_length):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(pwd_length))  # for a 20-character password
    
  def _get_cluster_token(self, prefix):
    cluster_token = ''
    Path('configs/rke2/tokens').mkdir(parents=True, exist_ok=True)
    token_fn = f'configs/rke2/tokens/{prefix}'
    if os.path.isfile(token_fn):
      print(f'Token file "{token_fn}" found in path, using it as cluster token')
      token_file = open(token_fn, 'r')
      cluster_token = token_file.read().strip()
      token_file.close()
    else:
      print(f'Token file "{token_fn}" does not found in path, generate random cluster token')
      cluster_token = self._generate_password(20)
      # save in to token file
      token_file = open(token_fn, 'w')
      token_file.write(cluster_token)
      token_file.close()
    return cluster_token

  def _write_rke2_config(self, fn, **kwargs):
    tpl = environment.get_template('templates/rke2_config.j2')
    Path('configs/rke2/configs').mkdir(parents=True, exist_ok=True)
    with open(f'configs/rke2/configs/{fn}.yaml', mode="w") as file:
      file.write(tpl.render(kwargs) + '\n')

  def create_rke_config(self):
    lb_ips = self.other_nodes ['load_balancers']
    backends = list(itertools.chain(*self.cluster_nodes['masters'].values())) + lb_ips + [self.lb_virtual_ip]
    shared_token = self._get_cluster_token('shared')
    agent_token = self._get_cluster_token('agent')
    # create primary primary config
    self._write_rke2_config('primary_masters', backends=backends)
    # create secondary masters config
    self._write_rke2_config('secondary_masters', backends=backends, lb_ip=self.lb_virtual_ip)
    # create workers config
    for worker_type in self.cluster_nodes['workers']:
      self._write_rke2_config(f'{worker_type}_workers', worker_type=worker_type, lb_ip=self.lb_virtual_ip)
        
service = AnsibleInventoryService()
service.create_haproxy_config()
service.create_inventories()
service.create_rke_config()
