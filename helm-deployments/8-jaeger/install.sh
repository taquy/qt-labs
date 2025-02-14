#!/bin/bash

ns="jaeger"
chart_name="jaeger"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

kubectl apply -f manifests/

# install or upgrade the helm charts
helm install \
  -f values/cassandra.yaml \
  -f values/opensearch.yaml \
  -f values/jaeger.yaml \
  -f values/zipkin.yaml \
  -f values/opentelemetry-collector.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/cassandra.yaml \
  -f values/opensearch.yaml \
  -f values/jaeger.yaml \
  -f values/zipkin.yaml \
  -f values/opentelemetry-collector.yaml \
  --namespace $ns $chart_name .
