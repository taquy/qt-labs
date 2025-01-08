#!/bin/bash

ns="otel-demo"
chart_name="otel-demo"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/opentelemetry-demo.yaml \
  -f values/opensearch.yaml \
  -f values/kafka.yaml \
  -f values/valkey.yaml \
  -f values/prometheus.yaml \
  -f values/jaeger.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/opentelemetry-demo.yaml \
  -f values/opensearch.yaml \
  -f values/kafka.yaml \
  -f values/valkey.yaml \
  -f values/prometheus.yaml \
  -f values/jaeger.yaml \
  --namespace $ns $chart_name .
