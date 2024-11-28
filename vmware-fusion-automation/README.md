# generate cluster token (only need to run once per cluster)
```sh
openssl rand -base64 12 > cluster_token
```

# get virtual ip address
```sh
# install nmap
brew install nmap

sudo python 1-collect-vmware-machines.py
```

# run setup script
```sh
# install python packages
pip install -r requirements.txt

# install
python create-inventory.py
```

# execute playbooks
```sh
ansible-playbook -i inventories.yaml -K playbooks/1-pre-installation.yaml
ansible-playbook -i inventories.yaml -K playbooks/2-setup-loadbalancer.yaml
ansible-playbook -i inventories.yaml -K playbooks/3.1-upload-tokens.yaml
ansible-playbook -i inventories.yaml -K playbooks/3.2-setup-masters.yaml
ansible-playbook -i inventories.yaml -K playbooks/3.3-setup-workers.yaml

ansible-playbook -i inventories.yaml -K \
  --extra-vars "local_kubeconfig_dir=$HOME" playbooks/4-download-kubeconfig.yaml
  
ansible-playbook -i inventories.yaml -K playbooks/5-uninstall-cluster.yaml
```