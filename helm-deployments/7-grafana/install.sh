#!/bin/bash

ns="grafana"
chart_name="grafana"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/alertmanager.yaml \
  -f values/grafana.yaml \
  -f values/loki.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/alertmanager.yaml \
  -f values/grafana.yaml \
  -f values/loki.yaml \
  --namespace $ns $chart_name .
