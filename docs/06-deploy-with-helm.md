# Time for Helm
From this point on, you could follow the [Getting started guide](https://docs.flyte.org/en/latest/deployment/deployment/cloud_simple.html) with some considerations:

1. Edit the `eks-starter.yaml` file replacing the values obtained during the previous steps in this tutorial:

```yaml
configuration:
  database:
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
2. Example output of the Helm install command:
```bash
$ helm install flyte-backend flyteorg/flyte-binary \        --namespace flyte --values eks-starter.yaml

NAME: flyte-backend
LAST DEPLOYED: Wed Mar 22 17:46:21 2023
NAMESPACE: flyte
STATUS: deployed
REVISION: 1
TEST SUITE: None
```
3. Wait a couple of minutes and check the status of the Flyte Pod (it should be `Running`):
```bash
$ kubectl get pods -n flyte

k get pods -n flyte

NAME                   READY       STATUS    RESTARTS             AGE
flyte-backend-flyte-binary-... 0/1  Running  0  8s
```
4. Create a `ClusterRoleBinding` to associate the Service Account created in Lab 3 with the ClusterRole created by Helm:
- Create a `clusterrb.yaml` file with the following contents, replacing the Service Account name:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: flyte-binary-cluster-role-binding
subjects:
- kind: ServiceAccount
  name: <my-flyte-sa> # Name is case sensitive
  apiGroup: ""
  namespace: flyte
roleRef:
  kind: ClusterRole
  name: flyte-backend-flyte-binary-cluster-role
  apiGroup: rbac.authorization.k8s.io%
```
- Create the resource:
```bash
    kubectl apply -f clusterrb.yaml
```
5. Verify the `insecure:` parameter is set to `true` in your `$HOME/.flyte/config.yaml` file to turn off SSL:
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
**NOTE**: if you plan to connect to Flyte using its gRPC interface, change `localhost` to the FQDN defined in Lab 5 and change the port to `8089`

6. Start the port-forward session as indicated in the [Getting Started guide](https://docs.flyte.org/en/latest/deployment/deployment/cloud_simple.html#port-forward-flyte-service) and trigger your [first workflow](https://docs.flyte.org/en/latest/deployment/deployment/cloud_simple.html#test-workflow)

> If you experience issues, review the [Troubleshooting guide](https://docs.flyte.org/en/latest/community/troubleshoot.html) or ask for help in the [#flyte-deployment](https://flyte-org.slack.com/archives/C01P3B761A6) channel