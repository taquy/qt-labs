#!/bin/bash

ns="otel-demo"
chart_name="apps"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/opentelemetry-demo.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/opentelemetry-demo.yaml \
  --namespace $ns $chart_name .
