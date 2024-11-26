import yaml

lb_ip_file = open('/tmp/loadbalancer_ip', 'r')
lb_ip = lb_ip_file.read().strip()
lb_ip_file.close()
with open('/etc/rancher/rke2/rke2.yaml') as stream:
  cfg = yaml.safe_load(stream)
  
cfg['clusters'][0]['cluster']['server'] = f'https://{lb_ip}:6443'
cfg['clusters'][0]['name'] = 'rke2'
cfg['contexts'][0]['context']['cluster'] = 'rke2'
cfg['contexts'][0]['name'] = 'rke2'

with open('/tmp/rke2.yaml', 'w') as outfile:
  yaml.dump(cfg, outfile, default_flow_style=False)
