# Add repo and get repository versions

```sh
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
# search for versions
helm search repo open-telemetry
```

# Setup values for OTEL demo

```sh
# get values
helm show values open-telemetry/opentelemetry-demo > values/default/opentelemetry-demo.yaml
cp values/default/opentelemetry-demo.yaml values/opentelemetry-demo.yaml
# generate Chart.lock
helm dep update
```
