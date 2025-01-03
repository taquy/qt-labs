#!/bin/bash

ns="otel-collector"
chart_name="otel-collector"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/opentelemetry-collector.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/opentelemetry-collector.yaml \
  --namespace $ns $chart_name .
