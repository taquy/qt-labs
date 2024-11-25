# generate cluster token (only need to run once)
openssl rand -base64 12 > cluster_token


# run setup script
python create-inventory.py


# execute playbooks
ansible-playbook playbooks/1-setup-loadbalancer.yaml -i inventories.yaml -K
ansible-playbook playbooks/2-install-cluster.yaml -i inventories.yaml -K
ansible-playbook playbooks/3-uninstall-cluster.yaml -i inventories.yaml -K
