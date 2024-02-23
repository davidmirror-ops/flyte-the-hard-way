# Install and Configure MikroK8s

To deploy Kubernetes on your Ubuntu-powered device install the microk8s snap.

> This tutorial uses the 1.25 channel version

```bash
sudo snap install microk8s --classic --channel=1.25
```

To enable the `microk8s` command for your current user, run the following commands:

```bash
sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube
newgrp microk8s
```

To validate the microk8s installation you can run the following command to display the current status of microk8s and enabled/disabled addons:

> After installing the microk8s snap it can take a couple of minutes until the status becomes healthy

```bash
microk8s status
```

If it successfully displays the microk8s status, you are ready to operate via `kubectl` like shown in the following example:

```bash
microk8s.kubectl get nodes
```

To not type `microk8s.kubectl` every time, feel free to use this alias:

```bash
echo 'alias kubectl="microk8s kubectl"' >> ~/.bashrc && source ~/.bashrc
```

---

Next: [deploy minio and postgres](03-deploy-minio-and-postgres.md)
