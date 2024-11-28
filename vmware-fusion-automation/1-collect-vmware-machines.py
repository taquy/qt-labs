import subprocess
import random
import yaml
from pathlib import Path

class VmwareCollector:
  vm_dir = "/Users/qt/Virtual Machines.localized"

  # collect nodes and group nodes master prefix is `m`, worker prefix is `w`
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
    'load_balancers': [],
    'dns': [],
  }
  api_servers = []
  virtual_ip = ''
  hosts_file_records = []

  def _add_worker_node(self, node_name, ip_addr):
    worker_types = {
      'm': 'memory',
      'c': 'compute',
      'd': 'disk',
      'g': 'generic',
    }
    worker_prefix = node_name.split('-')[1][0]
    node_type = worker_types[worker_prefix]
    self.worker_nodes[node_type].append(ip_addr)
    
  def _add_master_node(self, node_name, ip_addr):
      # create primary and secondary node group
      node_type = 'primary' if node_name == 'm1' else 'secondary'
      self.master_nodes[node_type].append(ip_addr)
      # configs for haproxy
      self.api_servers.append({
        'name': node_name,
        'ip_addr': ip_addr
      })
      
  def _set_virtual_ip(self, ip_addr):
    print('Getting virtual IP address...')
    cmd = "sudo nmap -v -sn -n " + ip_addr + "/24 -oG - | awk '/Status: Down/{print $2}'"
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    available_ips = ps.communicate()[0].decode('utf-8').strip().split('\n')[1:-1]
    self.virtual_ip = random.choice(available_ips)
    print(f'Virtual IP address found: {self.virtual_ip}')

  def _collect_vmware_inventories(self):
    for filepath in Path(self.vm_dir).glob('*vmwarevm'):
      fn = filepath.absolute()
      ip_addr = subprocess.run(['vmrun', 'getGuestIPAddress', fn], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
      node_name = Path(fn).stem
      # get virtual ip address from available ip in network
      if not self.virtual_ip:
        self._set_virtual_ip(ip_addr)
      # host file inventories
      self.hosts_file_records.append({
        'name': node_name, 
        'ip_addr': ip_addr
      })
      print(node_name, ip_addr)
      # categorize node lists and get available virtual ip
      if 'dns' in node_name:
        self.other_nodes['dns'].append(ip_addr)
      elif 'lb' in node_name:
        self.other_nodes['load_balancers'].append(ip_addr)
      else:
        node_prefix = node_name[0]
        if node_prefix == 'm':
          self._add_master_node(node_name, ip_addr)
        elif node_prefix == 'w':
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
      'hosts_file_records': self.hosts_file_records,
      'virtual_ip': self.virtual_ip
    }
    Path("configs").mkdir(parents=True, exist_ok=True)
    with open('configs/vm_lists.yaml', 'w') as outfile:
      yaml.dump({'hosts': vm_lists}, outfile, default_flow_style=False)
  
service = VmwareCollector()
service.start()
