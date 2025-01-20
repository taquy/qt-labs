https://docs.px.dev/installing-pixie/install-guides/self-hosted-pixie/#prerequisites

```sh
git clone https://github.com/pixie-io/pixie.git

cd pixie
export LATEST_CLOUD_RELEASE=$(git tag | perl -ne 'print $1 if /release\/cloud\/v([^\-]*)$/' | sort -t '.' -k1,1nr -k2,2nr -k3,3nr | head -n 1)
git checkout "release/cloud/v${LATEST_CLOUD_RELEASE}"

perl -pi -e "s|newTag: latest|newTag: \"${LATEST_CLOUD_RELEASE}\"|g" k8s/cloud/public/kustomization.yaml

# update domain names if needed (default: dev.withpixie.dev)
# new domain: pixie.cartrack.dev

k8s/cloud/public/base/proxy_envoy.yaml
k8s/cloud/public/base/domain_config.yaml
scripts/create_cloud_secrets.sh

# install mkcert: 
brew install mkcert
brew install nss
mkcert -install

kubectl create namespace plc
./scripts/create_cloud_secrets.sh

# sample outputs: Created a new certificate valid for the following names 📜
#  - "dev.withpixie.dev"
#  - "*.dev.withpixie.dev"
#  - "localhost"
#  - "127.0.0.1"
#  - "::1"

# install kustomize: https://kubectl.docs.kubernetes.io/installation/kustomize/binaries/
curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash

# generate manifests and apply
kustomize build k8s/cloud_deps/base/elastic/operator > 1-operators 
kubectl apply -f 1-operators.yaml

kustomize build k8s/cloud_deps/public > 2-deps.yaml
kubectl apply -f 2-deps.yaml

kustomize build k8s/cloud/public/ | kubectl apply -f -

# to delete
kustomize build k8s/cloud_deps/base/elastic/operator | kubectl delete -f -
kustomize build k8s/cloud_deps/public | kubectl delete -f -
kustomize build k8s/cloud/public/ | kubectl delete -f -

kubectl get pods -n plc

kubectl get service cloud-proxy-service -n plc
kubectl get service vzconn-service -n plc

go build src/utils/dev_dns_updater/dev_dns_updater.go
./dev_dns_updater --domain-name="dev.withpixie.dev"  --kubeconfig=$HOME/.kube/config --n=plc
```


```sh
mkdir -p manifests
kustomize build k8s/cloud_deps/public/postgres >  manifests/1-postgres.yaml
```
