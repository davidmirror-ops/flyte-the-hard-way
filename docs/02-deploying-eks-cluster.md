# Deploying an EKS cluster

1. Make sure that your system has these elements available:
- [kubectl](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html)
- [eksctl](https://docs.aws.amazon.com/eks/latest/userguide/eksctl.html)
- [awscli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Helm](https://helm.sh/docs/intro/install/) 
- openssl
- Access to the AWS console

2. Complete the awscli [quick configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-config)
3. Go to the AWS Management console > **Virtual Private Cloud** > **Subnets** and take note of all the Subnet IDs available in the supported Availability Zones on the VPC you plan to use to deploy Flyte:

![](subnets.png)

4. Go to the terminal and submit the command to create the EKS control plane, following these recommendations:
- Pick a Kubernetes version >= 1.19
- Give the cluster an informative name (eg. flyte-eks-cluster)

```bash
eksctl create cluster --name my-cluster --region region-code  --version 1.25 --vpc-private-subnets subnet-ID1,subnet-ID2 --without-nodegroup
```

After some time (minutes) the deployment should finish with an output similar to:

```bash
EKS cluster "my-cluster" in "region-code" region is ready
```
## Create an EKS node group
In this step we'll deploy the Kubernetes worker nodes where the actual workloads will run.

1. From the AWS Management console, go to **EKS**
2. Select the cluster you created in the previous section
3. Go to **Compute** and click on **Add node group**
4. Assign a name to the node group
5. In the **Node IAM role** menu, select the `<eks-node-role>` created in the Roles and Service accounts section
6. For learning purposes, do not use launch templates, labels or taints
7. Choose the default `Amazon Linux 2 (AL2_x86_x64)` **AMI type**
8. Use `On-demand` **Capacity type** 
9. Instance type and size can be chosen based on your devops requirements. Keep the default if in doubt
10. For **Node group scaling configuration** select:
    - **Desired size**: `10` 
    - **Minimum size**: `5`
    - **Maximum size**: `5`
11. Use the default subnets selected which you will choose based on your EKS cluster accessible subnets
12. Keep **Configure SSH access to nodes** disabled unless needed
13. Review the configuration and click **Create**

Learn more about [AWS managed node groups](https://docs.aws.amazon.com/eks/latest/userguide/managed-node-groups.html)

## Connecting to the EKS cluster
Now, you have to “let your terminal know” where’s the Kubernetes cluster you’re trying to connect to.

Use your AWS account access keys to run the following commands, updating the `kubectl` config and switching to the new EKS cluster context:

14. Store your AWS login information in environment variables so they can be grabbed by `awscli`:
```bash
export AWS_ACCESS_KEY_ID=<YOUR-AWS-ACCOUNT-ACCESS-KEY-ID>
export AWS_SECRET_ACCESS_KEY=<YOUR-AWS-SECRET-ACCESS-KEY>
export AWS_SESSION_TOKEN=<YOUR-AWS-SESSION-TOKEN>
```
15. Switch to the new EKS cluster’s context:

```bash
aws eks update-kubeconfig --name <my-cluster> --region <region>
```

16. Verify the context has switched:
```bash
$ kubectl config current-context
arn:aws:eks:<region>:<AWS_ACCOUNT_ID>:cluster/<Name-EKS-Cluster>
```
17. Verify there are no Pod resources created
```bash
$ kubectl get pods
No resources found in default namespace.
```
## Create an S3 bucket

This is the blob storage resource that will be used by FlytePropeller and DataCatalog to store metadata for versioning and other use cases.

18. From the AWS Management Console, go to **S3**
19. Create a bucket leaving **Block all public access** enabled
20. Choose the same region and VPC as your EKS cluster
21. Take note of the name as it will be used in your Helm `values` file
---
Next: [Configure roles and service accounts](03-roles-service-accounts.md)