# run setup script
```sh
# install nmap
brew install nmap

# install python packages
pip install -r requirements.txt

# get virtual ip address and vm machines descriptions
sudo python 1-collect-vmware-machines.py

# create inventories, variables and other configs
python 2-create-ansible-inventory.py
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
