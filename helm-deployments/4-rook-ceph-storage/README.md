
```sh
kubectl apply -f https://raw.githubusercontent.com/rook/rook/master/deploy/examples/crds.yaml

k delete -f https://raw.githubusercontent.com/rook/rook/release-1.12/deploy/examples/crds.yaml

kubectl label crd cephblockpoolradosnamespaces.ceph.rook.io app.kubernetes.io/managed-by=Helm --overwrite
kubectl annotate crd cephblockpoolradosnamespaces.ceph.rook.io meta.helm.sh/release-name=rook-ceph --overwrite
kubectl annotate crd cephblockpoolradosnamespaces.ceph.rook.io meta.helm.sh/release-namespace=rook-ceph --overwrite
```
