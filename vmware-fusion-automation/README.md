# generate cluster token (only need to run once)
openssl rand -base64 12 > cluster_token


# run setup script
python create-inventory.py


# execute playbooks
ansible-playbook -i inventories.yaml -K playbooks/1-setup-loadbalancer.yaml
ansible-playbook -i inventories.yaml -K playbooks/2-setup-masters.yaml
ansible-playbook -i inventories.yaml -K playbooks/3-setup-workers.yaml

ansible-playbook -i inventories.yaml -K \
  --extra-vars "local_kubeconfig_dir=$HOME" playbooks/4-download-kubeconfig.yaml
  
ansible-playbook -i inventories.yaml -K playbooks/5-uninstall-cluster.yaml
