#!/bin/bash

ns="jaeger"
chart_name="jaeger-opensearch"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/opensearch.yaml \
  -f values/opensearch-dashboards.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/opensearch.yaml \
  -f values/opensearch-dashboards.yaml \
  --namespace $ns $chart_name .
