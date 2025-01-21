# Preparation
```sh
# install qemu guest agent
apt -y install qemu-guest-agent
apt update

systemctl enable qemu-guest-agent
systemctl start qemu-guest-agent
systemctl status qemu-guest-agent

# change hostname (optional)
sudo hostnamectl set-hostname n1
sudo reboot

# set static ip address (optional)
sudo cp /etc/netplan/50-cloud-init.yaml /etc/netplan/50-cloud-init.yaml.bak
rm /etc/netplan/50-cloud-init.yaml
sudo cat /etc/netplan/50-cloud-init.yaml.bak

sudo cat > /etc/netplan/1-primary.yaml << EOL
network:
  ethernets:
    enp0s1:
      dhcp4: false
      addresses: [192.168.64.2/24]
      routes:
      - to: default
        via: 192.168.64.1
      nameservers:
        addresses: [8.8.8.8,8.8.4.4,192.168.64.1]
  version: 2
EOL
sudo chmod 600 /etc/netplan/1-primary.yaml
cat /etc/netplan/1-primary.yaml

sudo reboot
```


# Execute playbook
```sh
ansible-playbook playbook.yaml -i inventories.yaml \
  --extra-vars "ansible_user=qt" \
  --ask-become-pass
```