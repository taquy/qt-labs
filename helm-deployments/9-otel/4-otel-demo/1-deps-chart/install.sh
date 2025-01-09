#!/bin/bash

ns="otel-demo"
chart_name="deps"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

kubectl apply -f manifests

# install or upgrade the helm charts
helm install \
  -f values/opensearch.yaml \
  -f values/kafka.yaml \
  -f values/valkey.yaml \
  -f values/prometheus.yaml \
  -f values/jaeger.yaml \
  -f values/grafana.yaml \
  -f values/flagd.yaml \
  -f values/opentelemetry-collector.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/opensearch.yaml \
  -f values/kafka.yaml \
  -f values/valkey.yaml \
  -f values/prometheus.yaml \
  -f values/jaeger.yaml \
  -f values/grafana.yaml \
  -f values/flagd.yaml \
  -f values/opentelemetry-collector.yaml \
  --namespace $ns $chart_name .
