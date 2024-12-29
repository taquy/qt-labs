#!/bin/bash

ns="otel-system"
chart_name="otel-system"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/opentelemetry-operator.yaml \
  -f values/opentelemetry-collector.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/opentelemetry-operator.yaml \
  -f values/opentelemetry-collector.yaml \
  --namespace $ns $chart_name .
