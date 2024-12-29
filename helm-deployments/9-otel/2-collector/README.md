# Add repository

```sh
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts

# search for versions
helm search repo open-telemetry

# get values
helm show values open-telemetry/opentelemetry-collector > values/default/opentelemetry-collector.yaml
cp values/default/opentelemetry-collector.yaml values/opentelemetry-collector.yaml

# generate Chart.lock
helm dep update
```