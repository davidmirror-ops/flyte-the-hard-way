# Flyte The Hard Way 
This tutorial walks you through setting up Flyte in a semi-automated way. It includes all the manual steps you need to prepare the infrastructure before adjusting and installing a Helm chart. For a fast non-production setup, try [the Sandbox](https://docs.flyte.org/en/latest/deployment/deployment/sandbox.html).

> The steps described taken in this tutorial are not the only prescribed way to prepare the infrastructure or deploy Flyte. Feel free to contribute improvements or adapt it to your organization's policies and best practices.        

This guides takes inspiration from [Kubernetes The Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way)
## Target audience
This tutorial is intended for platform/infrastructure engineers who plan to support a Flyte environment for production or testing.

## Introduction
Flyte is a flexible and robust platform to develop and deploy machine learning workloads in a cloud-native environment. It facilitates interaction with the underlying Kubernetes infrastructure for users who are not entirely familiar with it.

To make Flyte work (especially for deployment), you’ll need to prepare the infrastructure layer.   

While the [official documentation](https://docs.flyte.org/en/latest/deployment/deployment/cloud_simple.html) covers the general process to deploy the single binary version, this tutorial aims to supplement docs with guidance to prepare the  for a successful installation of Flyte.


# Flyte on AWS

This tutorial will deploy Flyte single binary to an EKS environment, progressively adding features to reach a production-ready setup.

For the purposes of this basic tutorial, I adhered to the following principles:
- Keep all Flyte components in the same VPC
- Use default permissions when needed. More fine-grained access control can be defined and implemented by each organization
- Tag resources in accordance with your DevOps policies
- Deploy no SSL or Ingress. Follow parts 2 and 3 of this series to add those features 

## Part I: Simple deployment without SSL, Ingress or authentication
- Lab 1: [Configuring permissions on AWS](./docs/aws/01-eks-permissions.md)
- Lab 2: [Deploying an EKS cluster](./docs/aws/02-deploying-eks-cluster.md)
- Lab 3: [Configure roles and service accounts](./docs/aws/03-roles-service-accounts.md)
- Lab 4: [Create a relational database](./docs/aws/04-create-database.md)
- Lab 5: [Deploy with Helm](./docs/aws/05-deploy-with-helm.md) 
## Part II: Scalable networking with Ingress
- Lab 6: [Intro to Ingress and configuring the controller](./docs/aws/06-intro-to-ingress.md)
- Lab 7: [Configure SSL](./docs/aws/07-configure-SSL.md)
- Lab 8: [Adjust Helm values and upgrade the release](./docs/aws/08-adjust-values-upgrade-Helm.md)
- Lab 9: [Connect to Flyte through Ingress](./docs/aws/09-connect-Flyte-ingress.md)

## Part III: Securing the stack with authentication
- Lab 10: [Prepare your environment for auth using Okta](./docs/aws/10-prepare-for-auth.md)
- Lab 11: [Upgrade your Helm release to use auth](./docs/aws/11-upgrade-with-auth.md)

# Flyte on local Kubernetes 

In the following tutorials, you'll deploy the `flyte-binary` chart to different Kubernetes distributions running on-premises.
## microk8s on VMs or bare-metal
### Part I: Single node without Ingress
- Lab 1: [Deploy an on-prem K8s node](docs/on-premises/single-node/001-configure-single-node-k8s.md)
- Lab 2: [Configure dependencies and install Flyte](docs/on-premises/single-node/002-single-node-onprem-install.md)

## Part II: Multiple worker nodes and Ingress (coming soon)

## Part III: Auth (coming soon)
---
## microk8s on Raspberry Pi
### Part I: Simple deployment with no Ingress or auth
- Lab 1: [Prepare a Raspberry Pi for microk8s](docs/on-premises/microk8s/01-preparing-raspberry-pi.md)
- Lab 2: [Install & Configure microk8s](docs/on-premises/microk8s/02-install-configure-microk8s.md)
- Lab 3: [Install Minio & Postgres](docs/on-premises/microk8s/03-deploy-minio-and-postgres.md)
- Lab 4: [Install Flyte](docs/on-premises/microk8s/04-install-flyte.md)
## Part II: Adding Ingress, TLS & submitting workflows
- Lab 5: [Adding Ingress and TLS](docs/on-premises/microk8s/05-add-ingress-and-tls.md)
- Lab 6: [Submitting Workflows](docs/on-premises/microk8s/06-submitting-workflows.md)
---
## Flyte deployment options


- **Hosted sandbox** is available for free at [sandbox.union.ai](https://sandbox.union.ai) for a maximum of 4 hours. It includes a VS Code environment, Jupyter notebook and UI ready to get a quick feel of the platform.
- **Sandbox** deploys a local, minimal Flyte backend via a single command. It includes core services, but it doesn’t scale and supports only the necessary extensions to expose the core Flyte functionality.
- **Single binary** bundles console, admin, data-catalog and propeller services within a single binary that can be deployed to a production K8s environment or to a local test setup such as minikube. It uses a single Helm chart to reduce startup times and simplify deployment.
- **Core** is the fully fledged deployment with complete control over the configuration of each Flyte component, including production-grade features like federated authentication and Ingress networking.
 

