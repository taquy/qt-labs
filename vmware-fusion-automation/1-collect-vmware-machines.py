import subprocess
import random
import yaml
from pathlib import Path
import os
import paramiko

# create configs dir
Path('configs').mkdir(mode=0o770, parents=True, exist_ok=True)
os.system('chmod 777 configs')
os.system('chown -R qt configs')


with open("config.yaml") as stream:
  global_config = yaml.safe_load(stream)

class VmwareCollector:

  # collect nodes and group nodes master prefix is `m`, worker prefix is `w`
  master_nodes = {
    'primary': [], # first master node to be install with RKE
    'secondary': [], # other master nodes to be install with RKE
  }
  worker_nodes = {}
  other_nodes = {}
  api_servers = [] # for haproxy configs
  load_balancers = [] # for haproxy configs
  lb_virtual_ip = '' # for keepalived and rke2 configs
  lb_primary_nic = '' # for keepalived configs 
  hosts_file_records = [] # for updating /etc/hosts
  worker_hosts = [] # for variables in worker playbooks

  def _add_worker_node(self, node_name, ip_addr):
    worker_types = global_config.get('worker_types')
    node_type = 'generic'
    if len(node_name.split('-')) > 1:
      worker_prefix = node_name.split('-')[1][0]
      node_type = worker_types[worker_prefix]
    if node_type not in self.worker_nodes:
      self.worker_nodes[node_type] = []
    self.worker_nodes[node_type].append(ip_addr)
    self.worker_hosts.append({
      'name': node_name, 
      'ip_addr': ip_addr
    })
    
  def _add_master_node(self, node_name, ip_addr):
      # create primary and secondary node group
      node_type = 'primary' if node_name == 'm1' else 'secondary'
      self.master_nodes[node_type].append(ip_addr)
      self.api_servers.append({'name': node_name, 'ip_addr': ip_addr}) # configs for haproxy
  
  def _set_lb_primary_nic(self, ip_addr):
    fp = 'configs/haproxy/lb_primary_nic'
    if os.path.isfile(fp):
      print(f'Virtual IP already found \"{fp}\"')
      with open(fp, 'r') as stream:
        self.lb_primary_nic = stream.read()
      return
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip_addr, username=global_config.get('ssh_user'), key_filename=global_config.get('ssh_key')) # no passwd needed
    stdin, stdout, stderr = client.exec_command("ip addr | awk '/state UP/ {print $2}' | sed 's/.$//'")
    stdin.close()
    stdout.channel.recv_exit_status()
    self.lb_primary_nic = stdout.read().decode('utf-8').strip()
    client.close()
    print(f'Primary LB NIC found: {self.lb_primary_nic}')
    with open(fp, 'w') as outfile:
      outfile.write(self.lb_primary_nic)
    os.chmod(fp, 0o777)
  
  def _set_lb_virtual_ip(self, ip_addr):
    fp = 'configs/haproxy/lb_virtual_ip'
    if os.path.isfile(fp):
      print(f'Virtual IP already found \"{fp}\"')
      with open(fp, 'r') as stream:
        self.lb_virtual_ip = stream.read()
      return
    print('Getting virtual IP address...')
    cmd = "sudo nmap -v -sn -n " + ip_addr + "/24 -oG - | awk '/Status: Down/{print $2}'"
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    available_ips = ps.communicate()[0].decode('utf-8').strip().split('\n')[1:-1]
    self.lb_virtual_ip = random.choice(available_ips)
    print(f'Virtual IP address found: {self.lb_virtual_ip}')
    with open(fp, 'w') as outfile:
      outfile.write(self.lb_virtual_ip)
    os.chmod(fp, 0o777)
    
  def _add_other_nodes(self, node_name, ip_addr):
    other_nodes = global_config.get('other_nodes')
    for node_key in other_nodes:
      if node_key not in node_name:
        continue
      ansible_group = other_nodes[node_key]
      if ansible_group not in self.other_nodes:
        self.other_nodes[ansible_group] = []
      self.other_nodes[ansible_group].append(ip_addr)
      return True
    return False
  
  def _collect_vmware_inventories(self):
    vm_dir = global_config.get('vm_dir')
    for filepath in Path(vm_dir).glob('*vmwarevm'):
      fn = filepath.absolute()
      ip_addr = subprocess.run(['vmrun', 'getGuestIPAddress', fn], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
      node_name = Path(fn).stem
      # get virtual ip address from available ip in network
      if not self.lb_virtual_ip or not self.lb_primary_nic:
        Path('configs/haproxy').mkdir(mode=0o770, parents=True, exist_ok=True)
        self._set_lb_virtual_ip(ip_addr)
        self._set_lb_primary_nic(ip_addr)
      # host file inventories
      host_pair = {'name': node_name, 'ip_addr': ip_addr}
      self.hosts_file_records.append(host_pair)
      # categorize node lists and get available virtual ip
      if self._add_other_nodes(node_name, ip_addr):
        continue
      if 'lb' in node_name:
        # configs for keepalived
        self.load_balancers.append(host_pair) 
      else:    
        node_prefix = node_name[0]
        if node_prefix == 'm':
          self._add_master_node(node_name, ip_addr)
        else:
          self._add_worker_node(node_name, ip_addr)
    
  def start(self):
    self._collect_vmware_inventories()
    cluster_nodes = {
      'masters': self.master_nodes,
      'workers': self.worker_nodes,
    }
    vm_lists = {
      'cluster_nodes': cluster_nodes,
      'other_nodes': self.other_nodes,
      'api_servers': self.api_servers,
      'load_balancers': self.load_balancers,
    }
    # save vm lists
    fp = 'configs/vm_lists.yaml'
    with open(fp, 'w') as outfile:
      yaml.dump({'hosts': vm_lists}, outfile, default_flow_style=False)
    # save hosts variables
    with open('configs/hosts.yaml', 'w') as outfile:
      yaml.dump({'hosts': self.hosts_file_records}, outfile, default_flow_style=False)
    with open('configs/worker_hosts.yaml', 'w') as outfile:
      yaml.dump({'hosts': self.worker_hosts}, outfile, default_flow_style=False)
      
service = VmwareCollector()
service.start()
