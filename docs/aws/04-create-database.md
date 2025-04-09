# Create a relational database

In this section, you will create the database used by both the primary control plane service (FlyteAdmin) and the Flyte memoization service (Data Catalog).

1. From the AWS Management console go to **RDS**
2. Click on **Create database**
3. From the **Engine options** select `Aurora (PostgreSQL compatible)`
4. As of this writing, select the latest Postgres version below `15.x` 
5. Leave the **Templates** as `Production`
6. Change the **DB cluster identifier** to `flyteadmin`
7. Set the **Master username** to `flyteadmin`
8. Choose a **Master password** that you will later use in the Helm template
9. Pick an **Instance configuration** that reflect your DevOps policies. If in doubt, select the default option from **Burstable classes (includes t classes)**
10. Unless otherwise indicated by your organization's policies, select `Don't create an Aurora Replica` from the **Availability and durability** menu
11. In the **Connectivity** section
    - Select `Don't connect to an EC2 compute resoource`
    - Choose `IPv4` as **Network type**
    - Make sure to select the same **Virtual Private Cloud (VPC)** that your EKS cluster is in
    - Leave **Public access** by default (`No`)
    - In a separate tab, navigate to the EKS cluster page and make note of the security group attached to your cluster.
    - Go back to the RDS page and select the EKS cluster’s security group from the **Existing VPC security groups** dropdown menu (feel free to leave the default as well).
12. Under the top level **Additional configuration** (there’s a sub menu by the same name) set `flyteadmin` as **Initial database name**
13. Leave all the other settings as is and hit **Create**.

## Check connectivity to the RDS database from the EKS cluster

14. Oncre created, go to **RDS** > **Databases** and click on your database
15. Take note of the **Endpoint name** of Type `Writer instance` (`<flyteadmin.cluster-UID.region.rds.amazonaws>`) .   

We will use `pgsql-postgres-client` to verify DB connectivity:

16. Create a namespace for testing purposes:
```bash
kubectl create ns testdb
```
17. Run the following command with the database username and password you configured, and the **Endpoint name**:
```bash
kubectl run pgsql-postgresql-client --rm --tty -i --restart='Never' --namespace testdb --image docker.io/bitnami/postgresql:11.7.0-debian-10-r9 --env='PGPASSWORD=<Password>' --command -- psql --host <RDS-ENDPOINT-NAME> -U flyteadmin -d flyteadmin -p 5432
```
18. If things are working fine then you should drop into a `psql` command prompt after hitting Enter
19. Verify connection by entering:
```bash
\conninfo
```
Expected output:
```bash
flyteadmin=> \conninfo
You are connected to database "flyteadmin" as user "flyteadmin" on host "flyteadmin.cluster-....rds.amazonaws.com" at port "5432".
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256, compression: off)
```
20. Type `\q` to quit
21. In case there are connectivity issues, please check the security groups on the database and the EKS cluster.
22. Delete the test namespace:
```bash
kubectl delete namespace testdb
```
---
Next: [Deploy with Helm](05-deploy-with-helm.md)


