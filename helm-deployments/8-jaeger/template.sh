#!/bin/bash

ns="jaeger"
chart_name="jaeger"

# install or upgrade the helm charts
helm template \
  -f values/jaeger.yaml \
  -f values/zipkin.yaml \
  -f values/certs.yaml \
  --namespace $ns $chart_name . > template.yaml