#!/bin/bash

ns="prometheus"
chart_name="prometheus"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/prometheus.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/prometheus.yaml \
  --namespace $ns $chart_name .
