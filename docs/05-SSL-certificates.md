# SSL certificate
To establish a secure gRPC connection, you'll need an SSL certificate. In this section of the tutorial , we'll work with a self-signed certificate which is not considered truly secure as opposed to a proper certificate signed by a Certificate Authority. The recommended approach is to use secure certificates and it will be covered in further sections of this tutorial's repo.

## Self-signed certificate (insecure)

1. Create a `req.conf` file and configure the parameters to request a self-signed certificate:
```
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no
[req_distinguished_name]
C = US
ST = WA
L = Seattle
O = Flyte
OU = IT
CN = flyte.example.org
emailAddress = dummyuser@flyte.org
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names
[alt_names]
DNS.1 = flyte.example.org
```
**NOTE**: The `CN` or `[alt_names]` parameters should include the FQDN you'll use to connect to Flyte (`flyte.example.org` in the example above) and it should be resolvable by your operating system. For testing purposes you could use [nip.io](https://nip.io/) to handle DNS resolution even to 127.0.0.1 (eg. `flyte.127.0.0.1.nip.io` -> `127.0.0.1`)

2. Use `openssl` to generate the `key` and `crt` files:

```bash
openssl req -x509 -nodes -days 3649 -newkey rsa:2048 -keyout key.out -out crt.out -config req.conf -extensions 'v3_req'
```
3. Create the ARN for the certificate:
```bash
aws acm import-certificate --certificate fileb://crt.out --private-key fileb://key.out --region <REGION>
```
---
Next: [Deploy with Helm](06-deploy-with-helm.md)
