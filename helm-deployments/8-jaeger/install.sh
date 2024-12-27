#!/bin/bash

ns="jaeger"
chart_name="jaeger"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

chart_source=original
# chart_source=bitnami

# install or upgrade the helm charts
helm install \
  -f values/${chart_source}/jaeger.yaml \
  -f values/${chart_source}/zipkin.yaml \
  -f values/certs.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/${chart_source}/jaeger.yaml \
  -f values/${chart_source}/zipkin.yaml \
  -f values/certs.yaml \
  --namespace $ns $chart_name .
