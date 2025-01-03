#!/bin/bash

ns="otel-operator"
chart_name="otel-operator"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/opentelemetry-operator.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/opentelemetry-operator.yaml \
  --namespace $ns $chart_name .
