# Configuring permissions in AWS

In order to control Flyte's access to AWS resources, the following roles have to be created:

## EKS Cluster role

This role will be used by the Kubernetes control plane to handle its internal communication and also to manage features like autoscaling.

1. From the AWS Management console, go to **IAM**
2. Go to **Access Management** > **Roles** > **Create role**
3. Leave the default **Trusted entity type** (`AWS Service`)
4. From the Use case dropdown find and select **EKS** then **EKS-Cluster**
5. Ensure that the `AmazonEKSClusterPolicy` is selected
6. Select **Create the role without a permissions boundary**.
   Setting proper permissions restrictions is advisable, and it should be done in accordance with your organization's security policies. Check the [EKS Best Practices Guide](https://aws.github.io/aws-eks-best-practices/security/docs/iam/) for further reference.
7. Give the role an informative name and hit **Create role**

[Learn more about the EKS cluster role](https://docs.aws.amazon.com/eks/latest/userguide/service_IAM_role.html#create-service-role)

## EKS Node role

This role will be used by the Kubernetes worker nodes where the actual workloads will run.

1. From the AWS Management console, go to **IAM**
2. Go to **Access Management** > **Roles** > **Create role**
3. Leave the default **Trusted entity type** (`AWS Service`)
4. Select **EC2** as Use case
5. Choose the following policies:

- `AmazonEKSWorkerNodePolicy`
- `AmazonEC2ContainerRegistryReadOnly`
- `AmazonEKS_CNI_Policy`

5. Select **Create the role without a permissions boundary**.
   Setting proper permissions restrictions is advisable, and it should be done in accordance with your organization's security policies. Check the [EKS Best Practices Guide](https://aws.github.io/aws-eks-best-practices/security/docs/iam/) for further reference.
   Give the role an informative name and hit Create role

[Learn more about node roles](https://docs.aws.amazon.com/eks/latest/userguide/create-node-role.html)

---

Next: [Deploy an EKS cluster](02-deploying-eks-cluster.md)
