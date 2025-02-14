#!/bin/bash

ns="longhorn"
chart_name="longhorn"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/longhorn.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/longhorn.yaml \
  --namespace $ns $chart_name .
