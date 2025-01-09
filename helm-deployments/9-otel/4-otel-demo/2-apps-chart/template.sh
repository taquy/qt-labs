#!/bin/bash

ns="otel-demo"
chart_name="apps"

# install or upgrade the helm charts
helm template \
  -f values/opentelemetry-demo.yaml \
  --namespace $ns $chart_name . > template.yaml
