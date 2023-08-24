# Configure a local Kubernetes cluster

Out of the multiple ways to provision a Kubernetes cluster, this tutorial uses K3s for the following reasons:

* Includes the `local-path` CSI provisioner, useful to enable persistency for the stateful dependencies of Flyte (`minio` and `postgres`)
* Using VMs as nodes, provides a straightforward path to implement an architecture where the same steps can be followed with one or multiple physical machines acting as K8s worker nodes, facilitating networking and volume mounts, as opposed to having an additional container engine layer in the middle.

## Pre-requisites

- A Linux or macOS machine
- [`kubectl`](https://kubernetes.io/docs/tasks/tools/) to interact with the K8s cluster
- [`multipass`](https://multipass.run/install) to manage VMs

## Create a local Kubernetes cluster

1. Create a VM:

```bash
multipass launch --name k3s-master --mem 4G --disk 40G

```
NOTE: change the memory and disk resources as needed. These are minimums to run example workflows. See `multipass launch --help` for more options.

2. Once created, verify its configuration:
```bash
multipass info k3s-master
```
Example output:

```bash
Name:           k3s-master
State:          Running
IPv4:           192.168.64.3
                10.42.0.0
                10.42.0.1
Release:        Ubuntu 22.04.3 LTS
Image hash:     f29b6190d5e0 (Ubuntu 22.04 LTS)
CPU(s):         1
Load:           0.64 0.55 0.62
Disk usage:     9.4GiB out of 38.7GiB
Memory usage:   1.0GiB out of 3.8GiB
```

3. Deploy K3s on the VM:
```bash
 multipass exec k3s-master -- bash -c "curl -sfL https://get.k3s.io | sh -"
```
4. Once installed, retrieve the cluster's `kubeconfig` info:

```bash
multipass exec k3s-master -- bash -c "sudo cat /etc/rancher/k3s/k3s.yaml"
```
5. If this is the first time you connect to a Kubernetes cluster from your machine ir this is the only cluster you'll get access to, save the file to your machine and use the `KUBECONFIG` environment variable:

```bash
export KUBECONFIG=<path-to-your-k3s.yaml>
```
Otherwise, use the information from the `k3s.yaml` file and add it to your local `kubeconfig` (typically`$HOME/.kube/config`):

> NOTE: the Kubernetes `config` file follows YAML indentation rules. Make sure to follow them

- On the `clusters` section, add a new entry with the `certificate-authority-data` and `server`
- Replace the `default` name for `k3s-01` or other descriptive name for the cluster.

Example:
```yaml
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUJkakNDQVIyZ0F3SUJBZ0lCQURBS0JnZ3Foa2pPUFFRREFqQWpNU0V3SHdZRFZRUUREQmhyTTNNdGMyVnkKZG1WeUxXTmhRREUyT1RJd05EUTVNRFV3SGhjTk1qTXdPREUwTWpBeU9ESTFXaGNOTXpNd09ERXhNakF5T0RJMQpXakFqTVNFd0h3WURWUVFEREJock0zTXRjMlZ5ZG1WeUxXTmhRREUyT1RJd05EUTVNRFV3V1RBVEJnY3Foa2pPClBRSUJCZ2dxaGtqT1BRTUJCd05DQUFUMi9hbmdvQU1lc3lMS2Nlc0hkTGovQThkTXB5Sm9pRmtJM0VQcDFRaXYKdDltd1IzMDh4anNMRXd3Vlo5WFdtZi8wdE10UTZ0K0NwbXMzRTdQblpTZytvMEl3UURBT0JnTlZIUThCQWY4RQpCQU1DQXFRd0R3WURWUjBUQVFIL0JBVXdBd0VCL3pBZEJnTlZIUTRFRmdRVUFIZkdoT2JTKzVxRjh0SGNVenBvCjdSMjgyUXN3Q2dZSUtvWkl6ajBFQXdJRFJ3QXdSQUlnT0FZb3FVU2RreVlxcVhrTWYvdkc0RmtqdnRma0JyQm8KRHZiQ0pvd3YxUFFDSUNZbjBJZDNZR1JKVnBveTZ4ZWZyWmlwMGY0YUJnLzJtdzVJVnQ5dlk1L1EKLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo=
    server: https://192.168.64.3:6443
  name: k3s-01
```
- Scroll down to the `contexts` section and add a new context. Change the `user` and `context` names from `default` to something more descriptive:

```yaml
- context:
    cluster: k3s-01
    user: k3s
  name: k3s-01
```
- Scroll down to the `users` section and add a new entry. Make sure to set a `name` that matches the `user` field in the `context` you just created:

```yaml
- name: k3s
  user:
    client-certificate-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUJrVENDQVRlZ0F3SUJBZ0lJY3REK1Q4R096Q013Q2dZSUtvWkl6ajBFQXdJd0l6RWhNQjhHQTFVRUF3d1kKYXpOekxXTnNhV1Z1ZEMxallVQXhOamt5TURRME9UQTFNQjRYRFRJek1EZ3hOREl3TWpneU5Wb1hEVEkwTURneApNekl3TWpneU5Wb3dNREVYTUJVR0ExVUVDaE1PYzNsemRHVnRPbTFoYzNSbGNuTXhGVEFUQmdOVkJBTVRESE41CmMzUmxiVHBoWkcxcGJqQlpNQk1HQnlxR1NNNDlBZ0VHQ0NxR1NNNDlBd0VIQTBJQUJKUFRrWVhQdEN2QWU0Sk4KSWxIMmtWMzc2VFhFakkrTzVEbXM5a25OMWs2aXgwcmpKbU5SUG5oRUZ0TEpZVU02T1NlK25LUEpISmpQdHNxUgpwNTBtRXRXalNEQkdNQTRHQTFVZER3RUIvd1FFQXdJRm9EQVRCZ05WSFNVRUREQUtCZ2dyQmdFRkJRY0RBakFmCkJnTlZIU01FR0RBV2dCU3BpbHRoM1RXRjEwMkNHNnhDcjF2T2k4V3JmekFLQmdncWhrak9QUVFEQWdOSUFEQkYKQWlFQTdYa0FPWHkwQjM4RzE1NWw1bXdjRTlKVnJUWG1ESG05RkthaENiL2s5L0VDSUNXTmpYRFdzMGxSL1Z0cQorTUZFOWpGMHZyMVdxbTRMVmszRWpoOS95RHp5Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0KLS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUJlRENDQVIyZ0F3SUJBZ0lCQURBS0JnZ3Foa2pPUFFRREFqQWpNU0V3SHdZRFZRUUREQmhyTTNNdFkyeHAKWlc1MExXTmhRREUyT1RJd05EUTVNRFV3SGhjTk1qTXdPREUwTWpBeU9ESTFXaGNOTXpNd09ERXhNakF5T0RJMQpXakFqTVNFd0h3WURWUVFEREJock0zTXRZMnhwWlc1MExXTmhRREUyT1RJd05EUTVNRFV3V1RBVEJnY3Foa2pPClBRSUJCZ2dxaGtqT1BRTUJCd05DQUFTZXJ1M212bHlqY3lvV2NCWHVmOWpXY21ZWm01R3daM0owbGdHZXB5ZVoKMkdUQVdzSkdOVUlDWjc4MEJZYkVTUGNSWVNBdktLMnducVMrWEdBSHFSb3RvMEl3UURBT0JnTlZIUThCQWY4RQpCQU1DQXFRd0R3WURWUjBUQVFIL0JBVXdBd0VCL3pBZEJnTlZIUTRFRmdRVXFZcGJZZDAxaGRkTmdodXNRcTliCnpvdkZxMzh3Q2dZSUtvWkl6ajBFQXdJRFNRQXdSZ0loQUswamp6eFpIeXgwRVQ3WEM3QTVFL05ORmdIaEVBUUoKbkpmZVZINVZ4Tm4yQWlFQXJ5YnVZSVgxYURrdUpjczFJNFNNTzJ0aUxkSU41TWtpUGFmclR3clVRU2s9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
    client-key-data: LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSU9Qd1graWRoN2RjOVRmdURSVk9ERWIrRk10VU9hbDNZVVJmcGIxWTg2ZWpvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFazlPUmhjKzBLOEI3Z2swaVVmYVJYZnZwTmNTTWo0N2tPYXoyU2MzV1RxTEhTdU1tWTFFKwplRVFXMHNsaFF6bzVKNzZjbzhrY21NKzJ5cEdublNZUzFRPT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo=
```
- Save your changes

6. Switch your `kubectl` contex to the k3s cluster info you just added:
```bash
kubectl config use-context k3s-01
```
Example output:
```bash
Switched to context "k3s-01".
```
7. Test your connection:
```bash
kubectl get nodes
```
Example output:
```bash
NAME         STATUS   ROLES                  AGE   VERSION
k3s-master   Ready    control-plane,master   9d    v1.27.4+k3s1
```
---
Next: [configure dependencies and install Flyte](docs/on-premises/002-install-local-flyte.md)