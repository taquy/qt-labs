#!/bin/bash

ns="jaeger"
chart_name="jaeger-kafka"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/kafka.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/kafka.yaml \
  --namespace $ns $chart_name .
