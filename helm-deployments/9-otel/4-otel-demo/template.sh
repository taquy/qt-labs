#!/bin/bash

ns="otel-demo"
chart_name="otel-demo"

# install or upgrade the helm charts
helm template \
  -f values/opentelemetry-demo.yaml \
  -f values/opensearch.yaml \
  -f values/kafka.yaml \
  -f values/valkey.yaml \
  -f values/prometheus.yaml \
  -f values/jaeger.yaml \
  -f values/grafana.yaml \
  -f values/flagd.yaml \
  --namespace $ns $chart_name . > template.yaml

