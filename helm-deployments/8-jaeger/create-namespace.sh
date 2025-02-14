#!/bin/bash

declare -a namespaces=("jaeger")
for (( i=0; i<${#namespaces[@]}; i++ ));
do
  ns="${namespaces[$i]}"
  echo "Creating namesapce ${ns}"
  kubectl get namespace | grep -q "^$ns " || kubectl create namespace $ns
done
