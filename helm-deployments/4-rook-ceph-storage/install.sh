#!/bin/bash

ns="rook-ceph"
chart_name="rook-ceph"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# kubectl apply -f https://raw.githubusercontent.com/rook/rook/release-1.12/deploy/examples/crds.yaml

# install or upgrade the helm charts
helm install \
  -f values/rook-ceph.yaml \
  -f values/rook-ceph-cluster.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/rook-ceph.yaml \
  -f values/rook-ceph-cluster.yaml \
  --namespace $ns $chart_name .

# helm template \
#   -f values/rook-ceph.yaml \
#   -f values/rook-ceph-cluster.yaml . > template.yaml