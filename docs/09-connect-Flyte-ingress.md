## Connecting to Flyte through Ingress

1. From the **AWS Management Console** go to **Route 53**
2. Click on the hosted zone where you plan to create the DNS record
3. Click on **Create record**
4. Under **Record name** enter the domain name you used to request your certificate (`flyte-the-hard-way.uniondemo.run` in this tutorial)
5. From the **Record type** menu, select **CNAME**. This record type will allow you to redirect every request to the Ingress FQDN
6. From the command line, obtain the Ingress FQDN:
```bash
kubectl get ingress -n flyte
```
Example output:
```bash
NAME                              CLASS    HOSTS                              ADDRESS                                                      PORTS   AGE
flyte-backend-flyte-binary-grpc   <none>   flyte-the-hard-way.uniondemo.run   k8s-flyte-7fbf3d130b-550555649.<AWS_REGION>.elb.amazonaws.com   80      3h8m
flyte-backend-flyte-binary-http   <none>   flyte-the-hard-way.uniondemo.run   k8s-flyte-7fbf3d130b-550555649.<AWS_REGION>.elb.amazonaws.com   80      3h8m 
```
The FQDN corresponds to the `ADDRESS` value in the previous output.

7. Back at the **Route 53** GUI, paste the `ADDRESS` into the `Value` field
8. Click on **Create records**

**NOTE**: typically, DNS propagation takes about 60 seconds for Route 53 hosted zones. You can check status by selecting your DNS record and clicking on **View status**. It should be `INSYNC`.

9. Back at your terminal, find and edit you `$HOME/.flyte/config.yaml` file to reflect the following:
    
```yaml
admin:
  # For GRPC endpoints you might want to use dns:///flyte.myexample.com
  endpoint: dns:///flyte-the-hard-way.uniondemo.run #Replace with your domain name
  authType: Pkce
  insecure: false
  insecureSkipVerify: true
logger:
  show-source: true
  level: 6
```
10. Run your first workflow:

```bash
git clone https://github.com/flyteorg/flytesnacks
cd flytesnacks/cookbook
pyflyte run --remote core/flyte_basics/hello_world.py my_wf
```
Example output:

```bash
Go to https://flyte-the-hard-way.uniondemo.run/console/projects/flytesnacks/domains/development/executions/f7b562cecd41a44b4a17 to see execution in the console.
```

11. Paste the URL from the previous output in your browser:

![](/images/fthw-successful-execution.png)

## Closing remarks

**Congratulations!**

You have completed the process to deploy and configure a Flyte instance using Ingress networking and SSL. In the next section, we'll see how to configure authentication and authorization to improve the security posture of your deployment.

If you experience issues, check the [Troubleshooting section](https://docs.flyte.org/en/latest/community/troubleshoot.html)  or [#ask-the-community](https://flyte-org.slack.com/archives/CP2HDHKE1)
