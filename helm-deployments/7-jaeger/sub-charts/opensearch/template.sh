#!/bin/bash

ns="jaeger-opensearch"
chart_name="jaeger-opensearch"

# install or upgrade the helm charts
helm template \
  -f values/opensearch.yaml \
  -f values/opensearch-dashboards.yaml \
  --namespace $ns $chart_name . > template.yaml