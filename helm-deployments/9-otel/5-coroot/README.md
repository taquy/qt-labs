
```sh
# add repo
helm repo add coroot https://coroot.github.io/helm-charts

# get version
helm search repo coroot

# get default values
helm show values coroot/coroot > values/default/coroot.yaml

# port forward service
kubectl port-forward svc/coroot 8080:8080 -n mon-coroot

# username, password: admin/admin
```