#!/bin/bash

ns="jaeger-cassandra"
chart_name="jaeger-cassandra"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/cassandra.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/cassandra.yaml \
  --namespace $ns $chart_name .
