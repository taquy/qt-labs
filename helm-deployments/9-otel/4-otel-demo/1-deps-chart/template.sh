#!/bin/bash

ns="otel-demo"
chart_name="deps"

# install or upgrade the helm charts
helm template \
  -f values/opensearch.yaml \
  -f values/kafka.yaml \
  -f values/valkey.yaml \
  -f values/prometheus.yaml \
  -f values/jaeger.yaml \
  -f values/grafana.yaml \
  -f values/flagd.yaml \
  -f values/opentelemetry-collector.yaml \
  --namespace $ns $chart_name . > template.yaml
