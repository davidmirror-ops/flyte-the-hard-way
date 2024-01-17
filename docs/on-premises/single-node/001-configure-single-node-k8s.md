# Configure a single node Kubernetes cluster

By following this tutorial, you will deploy a Kubernetes cluster on a single VM.   
Feel free to skip this section if you already have a working Kubernetes environment.

> Do you plan to add more nodes/physical machines to your K8s environment? Then head over to the multi-node guide and start from there. **This guide doesn't currently provide a migration path from single-node to multi-node deployments**.

## Prerequisites

- A Linux or macOS machine
- [`kubectl`](https://kubernetes.io/docs/tasks/tools/) to interact with the K8s cluster
- [`multipass`](https://multipass.run/install) to manage VMs.

## Configuration process
> If you plan to run Flyte directly on bare-metal servers, just follow the microk8s [installation instructions](https://microk8s.io/docs/getting-started) and skip to step 3
1. Create the VM where you'll run Kubernetes:
``` bash
multipass launch --name k8smaster --memory 4G --disk 40G
```
2. Obtain the VM information. Take note of the IP address (typically the first on the list):
``` bash
multipass info k8smaster
```
Example output:
``` bash
Name:           k8smaster
State:          Running
IPv4:           192.168.64.12
                10.1.16.128
Release:        Ubuntu 22.04.3 LTS
Image hash:     f885a8e8f62a (Ubuntu 22.04 LTS)
CPU(s):         1
Load:           1.13 0.87 0.92
Disk usage:     5.2GiB out of 38.7GiB
Memory usage:   1.2GiB out of 3.8GiB
Mounts:         --
```
3. Start a shell on the VM:
``` bash
multipass exec k8smaster -- bash 
```
4. Install [microk8s](https://microk8s.io/):
``` bash
sudo snap install microk8s --classic
```
5. If you want to avoid adding sudo each time, make the `microk8s` command available to the `ubuntu` user:
``` bash
sudo usermod -a -G microk8s ubuntu
``` 
6. Once installed, obtain the K8s client config:
``` bash
cat /var/snap/microk8s/current/credentials/client.config
```
7. On a new terminal tab, open your kubectl config file (typically located at `$HOME/.kube/config`) and the the config for your new K8s instance:

- a. Add a new entry to the `clusters` section including the `certificate-authority-data` and `server`
- b. Replace the `server` IP with the IP for your machine/VM 

Example:
```yaml
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUJkakNDQVIyZ0F3SUJBZ0lCQURBS0JnZ3Foa2pPUFFRREFqQWpNU0V3SHdZRFZRUUREQmhyTTNNdGMyVnkKZG1WeUxXTmhRREUyT1RJd05EUTVNRFV3SGhjTk1qTXdPREUwTWpBeU9ESTFXaGNOTXpNd09ERXhNakF5T0RJMQpXakFqTVNFd0h3WURWUVFEREJock0zTXRjMlZ5ZG1WeUxXTmhRREUyT1RJd05EUTVNRFV3V1RBVEJnY3Foa2pPClBRSUJCZ2dxaGtqT1BRTUJCd05DQUFUMi9hbmdvQU1lc3lMS2Nlc0hkTGovQThkTXB5Sm9pRmtJM0VQcDFRaXYKdDltd1IzMDh4anNMRXd3Vlo5WFdtZi8wdE10UTZ0K0NwbXMzRTdQblpTZytvMEl3UURBT0JnTlZIUThCQWY4RQpCQU1DQXFRd0R3WURWUjBUQVFIL0JBVXdBd0VCL3pBZEJnTlZIUTRFRmdRVUFIZkdoT2JTKzVxRjh0SGNVenBvCjdSMjgyUXN3Q2dZSUtvWkl6ajBFQXdJRFJ3QXdSQUlnT0FZb3FVU2RreVlxcVhrTWYvdkc0RmtqdnRma0JyQm8KRHZiQ0pvd3YxUFFDSUNZbjBJZDNZR1JKVnBveTZ4ZWZyWmlwMGY0YUJnLzJtdzVJVnQ5dlk1L1EKLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo=
    server: https://192.168.64.12:16443
  name: microk8s
```
- c. Scroll down to the `contexts` section and add a new context. Leave the `user` as `admin` and make sure that the `cluster` field matches the `name` field in the previous step
```yaml
- context:
    cluster: microk8s
    user: admin
  name: microk8s
```
- d. Scroll down to the `users` section and add a new entry:

```yaml
- name: admin
  user:
    client-certificate-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUJrVENDQVRlZ0F3SUJBZ0lJY3REK1Q4R096Q013Q2dZSUtvWkl6ajBFQXdJd0l6RWhNQjhHQTFVRUF3d1kKYXpOekxXTnNhV1Z1ZEMxallVQXhOamt5TURRME9UQTFNQjRYRFRJek1EZ3hOREl3TWpneU5Wb1hEVEkwTURneApNekl3TWpneU5Wb3dNREVYTUJVR0ExVUVDaE1PYzNsemRHVnRPbTFoYzNSbGNuTXhGVEFUQmdOVkJBTVRESE41CmMzUmxiVHBoWkcxcGJqQlpNQk1HQnlxR1NNNDlBZ0VHQ0NxR1NNNDlBd0VIQTBJQUJKUFRrWVhQdEN2QWU0Sk4KSWxIMmtWMzc2VFhFakkrTzVEbXM5a25OMWs2aXgwcmpKbU5SUG5oRUZ0TEpZVU02T1NlK25LUEpISmpQdHNxUgpwNTBtRXRXalNEQkdNQTRHQTFVZER3RUIvd1FFQXdJRm9EQVRCZ05WSFNVRUREQUtCZ2dyQmdFRkJRY0RBakFmCkJnTlZIU01FR0RBV2dCU3BpbHRoM1RXRjEwMkNHNnhDcjF2T2k4V3JmekFLQmdncWhrak9QUVFEQWdOSUFEQkYKQWlFQTdYa0FPWHkwQjM4RzE1NWw1bXdjRTlKVnJUWG1ESG05RkthaENiL2s5L0VDSUNXTmpYRFdzMGxSL1Z0cQorTUZFOWpGMHZyMVdxbTRMVmszRWpoOS95RHp5Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0KLS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUJlRENDQVIyZ0F3SUJBZ0lCQURBS0JnZ3Foa2pPUFFRREFqQWpNU0V3SHdZRFZRUUREQmhyTTNNdFkyeHAKWlc1MExXTmhRREUyT1RJd05EUTVNRFV3SGhjTk1qTXdPREUwTWpBeU9ESTFXaGNOTXpNd09ERXhNakF5T0RJMQpXakFqTVNFd0h3WURWUVFEREJock0zTXRZMnhwWlc1MExXTmhRREUyT1RJd05EUTVNRFV3V1RBVEJnY3Foa2pPClBRSUJCZ2dxaGtqT1BRTUJCd05DQUFTZXJ1M212bHlqY3lvV2NCWHVmOWpXY21ZWm01R3daM0owbGdHZXB5ZVoKMkdUQVdzSkdOVUlDWjc4MEJZYkVTUGNSWVNBdktLMnducVMrWEdBSHFSb3RvMEl3UURBT0JnTlZIUThCQWY4RQpCQU1DQXFRd0R3WURWUjBUQVFIL0JBVXdBd0VCL3pBZEJnTlZIUTRFRmdRVXFZcGJZZDAxaGRkTmdodXNRcTliCnpvdkZxMzh3Q2dZSUtvWkl6ajBFQXdJRFNRQXdSZ0loQUswamp6eFpIeXgwRVQ3WEM3QTVFL05ORmdIaEVBUUoKbkpmZVZINVZ4Tm4yQWlFQXJ5YnVZSVgxYURrdUpjczFJNFNNTzJ0aUxkSU41TWtpUGFmclR3clVRU2s9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
    client-key-data: LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSU9Qd1graWRoN2RjOVRmdURSVk9ERWIrRk10VU9hbDNZVVJmcGIxWTg2ZWpvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFazlPUmhjKzBLOEI3Z2swaVVmYVJYZnZwTmNTTWo0N2tPYXoyU2MzV1RxTEhTdU1tWTFFKwplRVFXMHNsaFF6bzVKNzZjbzhrY21NKzJ5cEdublNZUzFRPT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo=
```
- e. Save your changes

Switch your `kubectl` contex to the new K8s cluster info you just added:
```bash
kubectl config use-context microk8s
```
Example output:
```bash
Switched to context "microk8s".
```
7. Test your connection:
```bash
kubectl get nodes
```
Example output:
```bash
NAME        STATUS   ROLES    AGE   VERSION
k8smaster   Ready    <none>   41h   v1.28.4
```
---
Next:  [configure dependencies and install Flyte](002-single-node-onprem-install.md)