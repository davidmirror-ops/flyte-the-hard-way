# Configure dependencies and install Flyte

This section assumes that you have a working Kubernetes environment.

You'll be configuring the external platform dependencies of Flyte:

- An S3-compliant object storage used for task metadata and to retrieve data to be processed by workflows.
- A relational database.

In this tutorial, we'll use Minio with a single bucket as the object storage provider and Postgres as the relational database. These two elements are configured to retain data even if the corresponding Pod is deleted.

> NOTE: this guide is intended for single-node K8s installations and doesn't provide migration instructions to switch to multi-node afterwards. If you plan to use multiple servers to run Flyte, go to the multi-node section and start from there.

1. Prepare your K8s cluster to provision Persistent Volumes:

```bash
microk8s enable hostpath-storage
```

> NOTE: for other K8s distributions, verify the provisioner available for local storage, typically associated with a StorageClass (`kubectl get storageclass`). If there isn't any, consider using [this implementation](https://github.com/rimusz/hostpath-provisioner) of the hostpath provisioner. To learn more about how Kubernetes handles data persistency, go to [the docs](https://kubernetes.io/docs/concepts/storage/persistent-volumes/).

> PersistentVolumeClaims created by the hostpath storage provisioner are bound to the local node, so **it is impossible to move them to a different node**.

2. Download the manifest that will provision the Flyte dependencies:

```bash
curl -sl https://raw.githubusercontent.com/davidmirror-ops/flyte-the-hard-way/main/docs/on-premises/single-node/manifests/local-flyte-resources.yaml > local-flyte-resources.yaml
```

3. Make sure to adjust sensitive values like `MINIO_ROOT_PASSWORD` and `POSTGRES_PASSWORD` before submitting the manifest:

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

4. Verify that both `minio` and `postgres` Pods are in `Running` state:

```bash
kubectl get pods -n flyte
```

Example output:

```bash
NAME                        READY   STATUS    RESTARTS   AGE
postgres-6f6bb8bff7-9sjnj   1/1     Running   0          75s
minio-7d795cd5d8-dlk54      1/1     Running   0          75s
```

5. In order to avoid saving the DB password in plain text to the `values` file, we leverage a recent addition to the `flyte-binary` chart that allows to consume pre-created secrets:

- Create an external secret containing the DB password:

> Replace `<POSTGRES_PASSWORD>` with what you configured on step 3

```yaml
cat <<EOF >local-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: flyte-binary-inline-config-secret
  namespace: flyte
type: Opaque
stringData:
  202-database-secrets.yaml: |
    database:
      postgres:
        password: <POSTGRES_PASSWORD>
EOF
```

- Submit the manifest:

```bash
kubectl create -f local-secret.yaml
```

- Describe the secret:

```bash
kubectl describe secret flyte-binary-inline-config-secret -n flyte
```

Example output:

```bash
Name:         flyte-binary-inline-config-secret
Namespace:    flyte
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
202-database-secrets.yaml:  48 bytes
```

6. Download the values file:

````bash
curl -sL https://raw.githubusercontent.com/davidmirror-ops/flyte-the-hard-way/main/docs/on-premises/single-node/manifests/local-values.yaml > local-values.yaml

7. Add the Flyte Helm repo:
```bash
helm repo add flyteorg https://flyteorg.github.io/flyte
````

8. Install Flyte:

```bash
helm install flyte-binary flyteorg/flyte-binary  --values local-values.yaml -n flyte
```

Example output:

```bash
NAME: flyte-binary
LAST DEPLOYED: Wed Aug 23 19:12:23 2023
NAMESPACE: flyte
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

9. Verify the `flyte-binary` Pod is in `Running` state:

```bash
kubectl get pods -n flyte
```

Example output:

```bash
NAME                            READY   STATUS    RESTARTS   AGE
postgres-6f6bb8bff7-9sjnj       1/1     Running   0          30m
minio-7d795cd5d8-dlk54          1/1     Running   0          30m
flyte-binary-58d779b9d8-z2hzs   1/1     Running   0          23s
```

10. Configure your Flyte config file for local connections (typically located at `$HOME/.flyte/config.yaml`):

> If you haven't done so, install `flytectl` so the config file is created. Check out the instructions [here](https://docs.flyte.org/en/latest/flytectl/overview.html#installation)

```yaml
admin:
  # For GRPC endpoints you might want to use dns:///flyte.myexample.com
  endpoint: localhost:8089
  authType: Pkce
  insecure: true
logger:
  show-source: true
  level: 6
```

11. Create a local DNS entry so the Flyte CLI connects to the `minio` service using its FQDN:

- In an OSX environment:

```bash
sudo vi /etc/hosts
```

- Add a new entry with the `minio` service name:

```bash
# Host Database
#
# localhost is used to configure the loopback interface
# when the system is booting.  Do not change this entry.
##
127.0.0.1       minio.flyte.svc.cluster.local
```

12. In three different terminal windows, start three port-forwarding sessions:

```bash
kubectl -n flyte port-forward service/minio 9000:9000
```

```bash
kubectl -n flyte port-forward service/flyte-binary-grpc 8089:8089
```

```bash
kubectl -n flyte port-forward service/flyte-binary-http 8088:8088
```

13. Save the following "hello world" workflow definition:

```bash
cat <<<EOF >hello_world.py
from flytekit import task, workflow
@task
def say_hello() -> str:
    return "hello world"
@workflow
def my_wf() -> str:
    res = say_hello()
    return res
if __name__ == "__main__":
    print(f"Running my_wf() {my_wf()}")
EOF
```

14. Execute the workflow on the Flyte cluster:

```bash
pyflyte run --remote hello_world.py my_wf
```

Example output:

```bash
Go to http://localhost:8089/console/projects/flytesnacks/domains/development/executions/f0c602e28c5c84d46b22 to see execution in the console.
```

> NOTE: different to what the CLI output indicates, use the `8088` port instead of 8089 to connect to the UI

15. Go to the Flyte console and monitor the execution:
    ![](../../images/local-flyte-ui.png)

---

**Congratulations!**
You have a working Flyte instance running on a local Kubernetes environment. Head over to the next sections to productionize your deployment.
