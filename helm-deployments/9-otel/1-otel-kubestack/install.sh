#!/bin/bash

ns="otel-kubestack"
chart_name="otel-kubestack"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/opentelemetry-kube-stack.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/opentelemetry-kube-stack.yaml \
  --namespace $ns $chart_name .
