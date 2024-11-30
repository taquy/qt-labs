#!/bin/bash

ns="network-system"
chart_name="network-system"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/metallb.yaml \
  --namespace $ns $chart_name .
  # helm upgrade --namespace $ns \
  # # -f values/zabbix.yaml \
  # $chart_name .
