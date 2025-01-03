#!/bin/bash

ns="prometheus"
chart_name="prometheus"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/kube-prometheus-stack.yaml \
  -f values/prometheus.yaml \
  -f values/alertmanager.yaml \
  -f values/alertmanager-snmp-notifier.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/kube-prometheus-stack.yaml \
  -f values/prometheus.yaml \
  -f values/alertmanager.yaml \
  -f values/alertmanager-snmp-notifier.yaml \
  --namespace $ns $chart_name .
