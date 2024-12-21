
# Sequence of deployment

1. Creating namespaces
```sh
bash create-namespace.sh
```

2. Render manifests (helm template) and review it in template.yaml
```sh
bash template.sh
```

3. Update secrets manifests and apply it
```sh
kubectl apply -f manifests
```

4. Install or upgrade the chart (if already deployed)

```sh
bash install.sh
```
