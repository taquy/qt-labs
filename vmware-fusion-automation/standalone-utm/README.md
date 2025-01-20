
apt update && apt -y install qemu-guest-agent

systemctl enable qemu-guest-agent
systemctl start qemu-guest-agent
systemctl status qemu-guest-agent

apt install network-manager -y
nmcli connection down enp0s1 && nmcli connection up enp0s1