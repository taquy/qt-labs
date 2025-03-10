#!/bin/bash

# install or upgrade the helm charts
helm template \
  -f values/coroot.yaml \
  -f values/coroot-operator.yaml . > template.yaml