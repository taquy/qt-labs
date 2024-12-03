#!/bin/bash

ns="nfs-storage"
chart_name="nfs-storage"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/nfs-subdir-external-provisioner.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/nfs-subdir-external-provisioner.yaml \
  --namespace $ns $chart_name .
