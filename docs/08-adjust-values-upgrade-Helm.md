## Adjust the values and upgrade the Helm release

In this section, you will use the results from the previous steps to update the `eks-production.yaml` values file.

1. Find and replace the values for the following keys in the `eks-production.yaml` file:

| Key | Value | Remarks  |
|---|---|---|
| `password`  |  RDS database password |  [See Lab 4](https://github.com/davidmirror-ops/flyte-the-hard-way/blob/main/docs/04-create-database.md)| 
| `host`  |  RDW writer instance name |  [See Lab 4](https://github.com/davidmirror-ops/flyte-the-hard-way/blob/main/docs/04-create-database.md#check-connectivity-to-the-rds-database-from-the-eks-cluster)  | 
|`dbname`|`flyteadmin`|[See Lab 4](https://github.com/davidmirror-ops/flyte-the-hard-way/blob/main/docs/04-create-database.md)|
|`metadataContainer`|S3 bucket to store metadata|[See Lab 2](https://github.com/davidmirror-ops/flyte-the-hard-way/blob/main/docs/02-deploying-eks-cluster.md#create-an-s3-bucket)|
|`userDataContainer`|S3 bucket where the user data resides|For learning purposes, it could be the same as `metadataContainer`|
|`region`|AWS region code||
|`auth` > `enabled`|Set to `false`|Auth will be configured in the next section|
|`production` >`defaultIamRole` > `value`|`arn:aws:iam::<AWS-ACCOUNT-ID>:role/flyte-system-role`|Repeat for the values under `staging` and `development` unless otherwise required by your DevOps policies|
|Under `serviceAccount` > `annotations`|`arn:aws:iam::<AWS-ACCOUNT-ID>:role/flyte-system-role`||

2. Under `database` add the following key:
    `username: flyteadmin`

This is done to adapt the chart to the specifics of the implementation of this tutorial.

3. Find the `ingress` section and set the `create` key to:

`create: true`

4. Under `commonAnnotations` remove any existing annotation refering to NGINX and replace with the following:

```yaml
  commonAnnotations:
    alb.ingress.kubernetes.io/certificate-arn: '<YOUR-SSL-CERTIFICATE-ARN>'
    alb.ingress.kubernetes.io/group.name: flyte
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS":443}]'
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/ssl-redirect: '443'
    alb.ingress.kubernetes.io/target-type: ip
    kubernetes.io/ingress.class: alb
```
For further reference about each annotation, visit the [ALB documentation](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.2/guide/ingress/annotations/)
    
5. Under `httpAnnotation` replace the existing NGINX annotation with the following:

```yaml
    alb.ingress.kubernetes.io/actions.app-root: '{"Type": "redirect", "RedirectConfig": {"Path": "/console", "StatusCode": "HTTP_302"}}'
```

6. Under `gRPCAnnotation` replace the existing NGINX annotation with:

```yaml
alb.ingress.kubernetes.io/backend-protocol-version: GRPC 
```
7. Replace the value of `host` with your domain name:

```yaml
host: flyte-the-hard-way.uniondemo.run
```
8. Unless you plan to use it right away, remove every reference to `spark` including the sections under `plugins`, `enabled-plugins` and `default-for-task-types`.
    
    
At this point, your `eks-production.yaml` should look similar to:
```yaml
configuration:
  database:
    username: flyteadmin
    password: <RDS-DB-PASSWORD>
    host: <RDS-WRITER-INSTANCE-NAME>
    dbname: flyteadmin
  storage:
    metadataContainer: <METADATA-S3-BUCKET>
    userDataContainer: <DATA-S3-BUCKET>
    provider: s3
    providerConfig:
      s3:
        region: "<aws-region>"
        authType: "iam"
  logging:
    level: 5
    plugins:
      cloudwatch:
        enabled: false
        templateUri: |-
          https://console.aws.amazon.com/cloudwatch/home?region=<AWS_REGION>#logEventViewer:group=/eks/opta-development/cluster;stream=var.log.containers.{{ .podName }}_{{ .namespace }}_{{ .containerName }}-{{ .containerId }}.log
  auth:
    enabled: false
    oidc:
      baseUrl: https://signin.hosted.unionai.cloud/oauth2/default
      clientId: <IDP_CLIENT_ID>
      clientSecret: <IDP_CLIENT_SECRET>
    internal:
      clientSecret: <CC_PASSWD>
      clientSecretHash: <HASHED_CC_PASSWD>
    authorizedUris:
    - https://flyte.company.com
  inline:
    task_resources:
      defaults:
        cpu: 100m
        memory: 100Mi
        storage: 100Mi
      limits:
        memory: 1Gi
    cluster_resources:
      customData:
      - production:
        - defaultIamRole:
            value: arn:aws:iam::<AWS-ACCOUNT-ID>:role/flyte-system-role
      - staging:
        - defaultIamRole:
            value: arn:aws:iam::<AWS-ACCOUNT-ID>:role/flyte-system-role
      - development:
        - defaultIamRole:
            value: arn:aws:iam::<AWS-ACCOUNT-ID>:role/flyte-system-role
    plugins:
      k8s:
        inject-finalizer: true
        default-env-vars:
          - AWS_METADATA_SERVICE_TIMEOUT: 5
          - AWS_METADATA_SERVICE_NUM_ATTEMPTS: 20
    storage:
      cache:
        max_size_mbs: 10
        target_gc_percent: 100
    tasks:
      task-plugins:
        enabled-plugins:
          - container
          - sidecar
          - K8S-ARRAY
        default-for-task-types:
          - container: container
          - container_array: K8S-ARRAY
clusterResourceTemplates:
  inline:
    001_namespace.yaml: |
      apiVersion: v1
      kind: Namespace
      metadata:
        name: '{{ namespace }}'
    010_spark_role.yaml: |
      apiVersion: rbac.authorization.k8s.io/v1
      kind: Role
      metadata:
        name: spark-role
        namespace: '{{ namespace }}'
      rules:
      - apiGroups:
        - ""
        resources:
        - pods
        - services
        - configmaps
        verbs:
        - '*'
    011_spark_service_account.yaml: |
      apiVersion: v1
      kind: ServiceAccount
      metadata:
        name: spark
        namespace: '{{ namespace }}'
        annotations:
          eks.amazonaws.com/role-arn: '{{ defaultIamRole }}'
    012_spark_role_binding.yaml: |
      apiVersion: rbac.authorization.k8s.io/v1
      kind: RoleBinding
      metadata:
        name: spark-role-binding
        namespace: '{{ namespace }}'
      roleRef:
        apiGroup: rbac.authorization.k8s.io
        kind: Role
        name: spark-role
      subjects:
      - kind: ServiceAccount
        name: spark
        namespace: '{{ namespace }}'
ingress:
  create: true
  commonAnnotations:
    alb.ingress.kubernetes.io/certificate-arn: 'arn:aws:acm:us-east-1:590375264460:certificate/e9618c54-0fd2-49ae-8c6a-279c47399070'
    alb.ingress.kubernetes.io/group.name: flyte
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS":443}]'
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/ssl-redirect: '443'
    alb.ingress.kubernetes.io/target-type: ip
    kubernetes.io/ingress.class: alb
  httpAnnotations:
    alb.ingress.kubernetes.io/actions.app-root: '{"Type": "redirect", "RedirectConfig": {"Path": "/console", "StatusCode": "HTTP_302"}}'
  grpcAnnotations:
    alb.ingress.kubernetes.io/backend-protocol-version: GRPC 
  host: flyte-the-hard-way.uniondemo.run #replace with your domain name
rbac:
  extraRules:
    - apiGroups:
      - ""
      resources:
      - pods
      - services
      - configmaps
      verbs:
      - "*"
    - apiGroups:
      - ""
      resources:
      - serviceaccounts
      verbs:
      - create
      - get
      - list
      - patch
      - update
    - apiGroups:
      - rbac.authorization.k8s.io
      resources:
      - rolebindings
      - roles
      verbs:
      - create
      - get
      - list
      - patch
      - update
    - apiGroups:
      - sparkoperator.k8s.io
      resources:
      - sparkapplications
      verbs:
      - "*"
serviceAccount:
  create: true 
  annotations:
    eks.amazonaws.com/role-arn: "arn:aws:iam::<AWS-ACCOUNT-ID>:role/flyte-system-role"
```
9. Upgrade the Helm chart with the new values file (or install it in case it hasn't been deployed already):

```bash
 helm upgrade flyte-backend flyteorg/flyte-binary -n flyte --values eks-production.yaml --install
```
10. After a couple of minutes, you should be able to query the Flyte pod:
```bash
kubectl get pod -n flyte
    
NAME                                          READY   STATUS    RESTARTS   AGE
flyte-backend-flyte-binary-56d5cc7957-79bjs   1/1     Running   0          3m10s
```
___
Next: [connect to Flyte throug Ingress](09-connect-Flyte-ingress.md)
