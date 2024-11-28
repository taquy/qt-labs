# generate cluster token (only need to run once per cluster)
```sh
openssl rand -base64 12 > cluster_token
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
ansible-playbook -i inventories.yaml -K playbooks/3-setup-masters.yaml
ansible-playbook -i inventories.yaml -K playbooks/4-setup-workers.yaml

ansible-playbook -i inventories.yaml -K \
  --extra-vars "local_kubeconfig_dir=$HOME" playbooks/5-download-kubeconfig.yaml
  
ansible-playbook -i inventories.yaml -K playbooks/6-uninstall-cluster.yaml
```