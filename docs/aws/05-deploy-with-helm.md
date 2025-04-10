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
    cluster_resources:
      customData:
      - production:
        - defaultIamRole:
            value: arn:aws:iam::<AWS-ACCOUNT-ID>:role/flyte-workers-role
      - staging:
        - defaultIamRole:
            value: arn:aws:iam::<AWS-ACCOUNT-ID>:role/flyte-workers-role
      - development:
        - defaultIamRole:
            value: arn:aws:iam::<AWS-ACCOUNT-ID>:role/flyte-workers-role
    task_resources:
      defaults:
        cpu: 500m
        memory: 500Mi
        storage: 500Mi
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
clusterResourceTemplates:
  inline:
    001_namespace.yaml: |
      apiVersion: v1
      kind: Namespace
      metadata:
        name: '{{ namespace }}'
    002_serviceaccount.yaml: |
      apiVersion: v1
      kind: ServiceAccount
      metadata:
        name: default
        namespace: '{{ namespace }}'
        annotations:
          eks.amazonaws.com/role-arn: '{{ defaultIamRole }}'
serviceAccount:
  create: enable
  annotations:
    eks.amazonaws.com/role-arn: "arn:aws:iam::<aws-account-id>:role/flyte-system-role"
```

5. Install the Helm chart:
```bash
helm install flyte-backend flyteorg/flyte-binary --namespace flyte --values eks-starter.yaml --create-namespace
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

The steps above can be deployed in CDK:

```ts
this.cluster.addManifest('flyte-namespace', {
  apiVersion: 'v1',
  kind: 'Namespace',
  metadata: {
    name: 'flyte',
  },
});

const flyteChart = cluster.addHelmChart('Flyte', {
  repository: 'https://flyteorg.github.io/flyte/',
  chart: 'flyte-binary',
  release: 'flyte-backend',
  version: '1.15.0',
  namespace: 'flyte',
  wait: true,
  timeout: Duration.minutes(15),
  values: {
    configuration: {
      database: {
        username: 'flyteadmin',
        password: <database-password>,
        host: database.clusterEndpoint.hostname,
        dbname: 'flyteadmin',
      },
      storage: {
        metadataContainer: bucket.bucketName,
        userDataContainer: bucket.bucketName,
        provider: 's3',
        providerConfig: {
          s3: {
            region: this.cluster.env.region,
            authType: 'iam',
          },
        },
      },
      inline: {
        cluster_resources: {
          customData: [
            {
              production: [
                {
                  defaultIamRole: {
                    value: flyteWorkersRole.roleArn,
                  },
                },
              ],
            },
            {
              staging: [
                {
                  defaultIamRole: {
                    value: flyteWorkersRole.roleArn,
                  },
                },
              ],
            },
            {
              development: [
                {
                  defaultIamRole: {
                    value: flyteWorkersRole.roleArn,
                  },
                },
              ],
            },
          ],
        },
        plugins: {
          k8s: {
            'inject-finalizer': true,
            'default-env-vars': [{ AWS_METADATA_SERVICE_TIMEOUT: 5 }, { AWS_METADATA_SERVICE_NUM_ATTEMPTS: 20 }],
          },
        },
        storage: {
          cache: {
            max_size_mbs: 100,
            target_gc_percent: 100,
          },
        },
        tasks: {
          'task-plugins': {
            'enabled-plugins': ['container', 'sidecar', 'K8S-ARRAY', 'agent-service', 'echo'],
            'default-for-task-types': [{ container: 'container' }, { container_array: 'K8S-ARRAY' }],
          },
        },
      },
    },
    clusterResourceTemplates: {
      inline: {
        '001_namespace.yaml': `apiVersion: v1
kind: Namespace
metadata:
  name: '{{ namespace }}'`,
        '002_serviceaccount.yaml': `apiVersion: v1
kind: ServiceAccount
metadata:
  name: default
  namespace: '{{ namespace }}'
  annotations:
    eks.amazonaws.com/role-arn: '{{ defaultIamRole }}'`,
      },
    },
    ingress: {
      create: true,
    },
    serviceAccount: {
      create: 'enable',
      annotations: {
        'eks.amazonaws.com/role-arn': flyteSystemRole.roleArn,
      },
    },
  },
});
```


7. Wait a couple of minutes and check the status of the Flyte Pod (it should be `Running`):
```bash
$ kubectl get pods -n flyte

k get pods -n flyte

NAME                   READY       STATUS    RESTARTS             AGE
flyte-backend-flyte-binary-... 1/1  Running  0  8s
```

8. Verify the IAM annotation is set in the Service Account:
```bash
kubectl describe sa flyte-backend-flyte-binary  -n flyte

Name:                flyte-backend-flyte-binary
Namespace:           flyte
Labels:              app.kubernetes.io/instance=flyte-backend
                     app.kubernetes.io/managed-by=Helm
                     app.kubernetes.io/name=flyte-binary
                     app.kubernetes.io/version=1.16.0
                     helm.sh/chart=flyte-binary-v1.3.0
Annotations:         eks.amazonaws.com/role-arn: arn:aws:iam::<account-id>:role/flyte-system-role
                     meta.helm.sh/release-name: flyte-backend
                     meta.helm.sh/release-namespace: flyte
Image pull secrets:  <none>
Mountable secrets:   <none>
Tokens:              <none>
Events:              <none>
```

10. Verify the `insecure:` parameter is set to `true` in your `$HOME/.flyte/config.yaml` file to turn off SSL:
```yaml
admin:
  # For GRPC endpoints you might want to use dns:///flyte.myexample.com
  endpoint: dns:///localhost:8089
  authType: Pkce
  insecure: true
logger:
  show-source: true
  level: 0
```
>NOTE: this configuration is used for the `flytectl/pyflyte` tools. The console (UI) connection is not controlled by the settings on this file.

11. Start the port-forward session:

```bash
kubectl -n flyte port-forward service/flyte-backend-flyte-binary 8088:8088 8089:8089
```

12. Run your [first workflow](https://docs.flyte.org/en/latest/deployment/deployment/cloud_simple.html#test-workflow)
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

___
Next: [productionize your deployment with Ingress and SSL](06-intro-to-ingress.md)
