import subprocess
import random
import yaml
from pathlib import Path
import os
import paramiko
import re

master_nodes = []
worker_nodes = []
output = subprocess.run(['utmctl', 'list'], stdout=subprocess.PIPE, text=True).stdout
lines = list(output.split('\n'))[1:]
for idx, line in enumerate(lines):
  elements = re.split(r'\s+', line)
  if len(elements) > 1 and 'started' in elements:
    node_name = elements[-1]
    cmd = subprocess.run(['utmctl', 'ip-address', node_name], stdout=subprocess.PIPE)
    ip_addr = cmd.stdout.decode('utf-8').strip().split('\n')[0]
    
    # first node is going to be master, the rest are worker
    if idx == 1:
      master_nodes.append(ip_addr)
    else:
      worker_nodes.append(ip_addr)
    print(idx, node_name, ip_addr)
    
master_nodes_obj = {ip: "" for ip in master_nodes}
worker_nodes_obj = {ip: "" for ip in worker_nodes}

inventories = {
    'master_nodes': {'hosts': master_nodes_obj},
    'workers': {'hosts': worker_nodes_obj},
}

with open('inventories.yaml', 'w') as file:
  yaml.dump(inventories, file)
