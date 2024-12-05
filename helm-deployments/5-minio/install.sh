#!/bin/bash

ns="minio"
chart_name="minio"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/minio.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/minio.yaml \
  --namespace $ns $chart_name .

kubectl apply -f manifests
