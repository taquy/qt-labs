# NFS Storage

## Setup NFS Storage

```bash
./add-nfs-dir.sh
```

## Install NFS Storage

```bash
./install.sh
```

## Uninstall NFS Storage

```bash
helm uninstall nfs-storage -n nfs-storage
```

## View NFS logs

```bash
kubectl logs -f -n nfs-storage -l app.kubernetes.io/name=nfs-subdir-external-provisioner
```
