# Add repo and get repository versions

```sh
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
# search for versions
helm search repo open-telemetry
```

# Setup values for OTEL operator

```sh
# get values
helm show values open-telemetry/opentelemetry-operator > values/default/opentelemetry-operator.yaml
cp values/default/opentelemetry-operator.yaml values/opentelemetry-operator.yaml
# generate Chart.lock
helm dep update
```

# Setup values for OTEL collector

```sh
# get values
helm show values open-telemetry/opentelemetry-collector > values/default/opentelemetry-collector.yaml
cp values/default/opentelemetry-collector.yaml values/opentelemetry-collector.yaml
# generate Chart.lock
helm dep update
```
