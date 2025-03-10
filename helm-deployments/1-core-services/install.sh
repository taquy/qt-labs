#!/bin/bash

ns="core-services"
chart_name="core-services"
kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns

# install or upgrade the helm charts
helm install \
  -f values/reflector.yaml \
  -f values/metallb.yaml \
  -f values/cert-manager.yaml \
  -f values/traefik.yaml \
  -f values/external-secrets.yaml \
  --namespace $ns $chart_name . ||
  helm upgrade --namespace $ns \
  -f values/reflector.yaml \
  -f values/metallb.yaml \
  -f values/cert-manager.yaml \
  -f values/traefik.yaml \
  -f values/external-secrets.yaml \
  --namespace $ns $chart_name .

sleep 5

kubectl apply -f manifests
