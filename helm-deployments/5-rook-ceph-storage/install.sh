#!/bin/bash

ns="rook-ceph-storage"
chart_name="rook-ceph-storage"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/rook-ceph.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/rook-ceph.yaml \
  --namespace $ns $chart_name .
