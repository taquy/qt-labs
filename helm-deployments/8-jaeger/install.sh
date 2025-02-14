#!/bin/bash

ns="jaeger"
chart_name="jaeger"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/jaeger.yaml \
  -f values/jaeger-operator.yaml \
  -f values/zipkin.yaml \
  -f values/certs.yaml \
  -f values/opentelemetry-collector.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/jaeger.yaml \
  -f values/jaeger-operator.yaml \
  -f values/zipkin.yaml \
  -f values/certs.yaml \
  -f values/opentelemetry-collector.yaml \
  --namespace $ns $chart_name .
