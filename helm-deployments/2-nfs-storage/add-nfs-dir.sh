#!/bin/bash

# Create NFS storage directory
sudo mkdir -p /nfs-storage
sudo chmod 777 /nfs-storage

# Add NFS export configuration if not exists
EXPORT_LINE='/nfs-storage *(rw,sync,no_subtree_check)'
if ! grep -qF "$EXPORT_LINE" /etc/exports; then
    echo "$EXPORT_LINE" | sudo tee -a /etc/exports
fi

# Refresh NFS exports
sudo exportfs -r
