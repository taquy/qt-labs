#!/bin/bash

ns="mon-coroot"
chart_name="coroot"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/coroot.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/coroot.yaml \
  --namespace $ns $chart_name .
