# Deploy Minio and Postgres

Two of the external platform dependencies of Flyte are:

- An S3-compliant object storage used for task metadata and to retrieve data to be processed by workflows. This tutorial uses minio.
- A postgres database.

These two elements are configured to retain data via Persistent Volumes even if the corresponding Pod is deleted. To make use of Persisten Volumes activate the `hostpath-storage` addon of microk8s.

```bash
microk8s enable hostpath-storage
```

> PersistentVolumeClaims created by the hostpath storage provisioner are bound to the local node!

Download the manifest that will provision the Flyte dependencies:

```bash
curl -sl https://raw.githubusercontent.com/davidmirror-ops/flyte-the-hard-way/main/docs/on-premises/microk8s/manifests/local-flyte-resources.yaml > local-flyte-resources.yaml
```

Make sure to adjust sensitive values like `MINIO_ROOT_PASSWORD` and `POSTGRES_PASSWORD` before submitting the manifest:

```bash
kubectl apply -f local-flyte-resources.yaml
```

Example output:

```bash
namespace/flyte created
persistentvolumeclaim/postgresql-pvc created
persistentvolumeclaim/minio-pvc created
service/postgres created
deployment.apps/postgres created
deployment.apps/minio created
service/minio created
```

Verify that both `minio` and `postgres` Pods are in `Running` state:

```bash
kubectl get pods -n flyte
```

Example output:

```bash
NAME                        READY   STATUS    RESTARTS   AGE
postgres-6f6bb8bff7-9sjnj   1/1     Running   0          75s
minio-7d795cd5d8-dlk54      1/1     Running   0          75s
```

You should be able to access the minio UI using the configured node port from any device in the local network in the browser:

```bash
http://<your-ubuntu-server-local-ip>:30088/login
```

---

Next: [install flyte](04-install-flyte.md)
