# Time for Helm
From this point on, you could follow the [Getting started guide](https://docs.flyte.org/en/latest/deployment/deployment/cloud_simple.html) with some considerations:

1. Add the Flyte chart repo to Helm:

```bash
helm repo add flyteorg https://flyteorg.github.io/flyte
```

2. Download the `eks-starter` values file:
```bash
curl -sL https://raw.githubusercontent.com/flyteorg/flyte/master/charts/flyte-binary/eks-starter.yaml > eks-starter.yaml
```
3. Edit the `eks-starter.yaml` file replacing the values obtained during the previous steps in this tutorial

4. If not present, add the `username: flyteadmin` field under the `database` section. Your `eks-starter.yaml` should ressemble the following:

```yaml
configuration:
  database:
    username: flyteadmin
    password: <database-password>
    host: <RDS-writer-endpoint-name>
    dbname: flyteadmin  
  storage:
    metadataContainer: <s3-bucket-for-metadata>
    userDataContainer: <s3-user-data-bucket>
    provider: s3
    providerConfig:
      s3:
        region: "<aws-region-code>"
        authType: "iam"
  inline:
    plugins:
      k8s:
        inject-finalizer: true
        default-env-vars:
          - AWS_METADATA_SERVICE_TIMEOUT: 5
          - AWS_METADATA_SERVICE_NUM_ATTEMPTS: 20
    storage:
      cache:
        max_size_mbs: 100
        target_gc_percent: 100
serviceAccount:
  create: false #disable serviceAccount creation as it was already created in Lab #3
  annotations:
  eks.amazonaws.com/role-arn: "arn:aws:iam::<aws-account-id>:role/flyte-system-role"
```

5. Install the Helm chart:
```bash
helm install flyte-backend flyteorg/flyte-binary --namespace flyte --values eks-starter.yaml
```

6. Example output of the Helm install command:
```bash
NAME: flyte-backend
LAST DEPLOYED: Wed Mar 22 17:46:21 2023
NAMESPACE: flyte
STATUS: deployed
REVISION: 1
TEST SUITE: None
```
7. Wait a couple of minutes and check the status of the Flyte Pod (it should be `Running`):
```bash
$ kubectl get pods -n flyte

k get pods -n flyte

NAME                   READY       STATUS    RESTARTS             AGE
flyte-backend-flyte-binary-... 0/1  Running  0  8s
```
8. Verify the `insecure:` parameter is set to `true` in your `$HOME/.flyte/config.yaml` file to turn off SSL:
```yaml
admin:
  # For GRPC endpoints you might want to use dns:///flyte.myexample.com
  endpoint: dns:///localhost:8088
  authType: Pkce
  insecure: true
logger:
  show-source: true
  level: 0
```
**NOTE**: if you plan to connect to Flyte using its gRPC interface, change the port to `8089`

9. Start the port-forward session:

```bash
kubectl -n flyte port-forward service/flyte-backend-flyte-binary 8088:8088 8089:8089
```

10. Run your [first workflow](https://docs.flyte.org/en/latest/deployment/deployment/cloud_simple.html#test-workflow)
____

## Uninstalling Flyte

1. Uninstall the Helm release:
```bash
helm uninstall flyte-backend flyteorg/flyte-binary --namespace flyte
```
2. Delete the `flyte` namespace:
```bash
kubectl delete ns flyte
```
_____
> If you experience issues, review the [Troubleshooting guide](https://docs.flyte.org/en/latest/community/troubleshoot.html) or ask help in the [#flyte-deployment](https://flyte-org.slack.com/archives/C01P3B761A6) channel