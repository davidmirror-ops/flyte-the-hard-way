## Configure SSL

In order to use SSL (required to use gRPC clients), you must create an SSL certificate. You may need to work with your infrastructure team to acquire a legitimate certificate, so the first set of instructions help you get going with a self-signed certificate. These certificates are not considered secure and **will show up as a security warning to any users in the Flyte console**, so it's recommended to procure a legitimate certificate as soon as possible.

### Self-signed method (insecure)

In this section, you will generate a self signed cert using `openssl` and obtain the <KEY> and <CRT> file:
    
11. Create a `req.conf` file with the following contents:
    
```bash
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
CN = flyte-the-hard-way.uniondemo.run
emailAddress = dummyuser@flyte.org
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names
[alt_names]
DNS.1 = flyte-the-hard-way.uniondemo.run
```
**NOTE**: remember to replace both the `CN` and `DNS.1` values with your domain name
    
12. Use `openssl` to generate the KEY and CRT files:
```bash
openssl req -x509 -nodes -days 3649 -newkey rsa:2048 -keyout key.out -out crt.out -config req.conf -extensions 'v3_req'
```

13. Import the certificate to AWS Certificate Manager (ACM) and take note of the ARN:

```bash
aws acm import-certificate --certificate fileb://crt.out --private-key fileb://key.out --region <REGION>
```
Example output:

```bash
{
    "CertificateArn": "arn:aws:acm:us-east-1:<AWS_ACCOUNT_ID>:certificate/e9618c54-0fd2-49ae-8c6a-279c47399070>:certificate/e9618c54-0fd2-49ae-8c6a-279c47399070"
}
(END)
```
### Production
    
Generate a certificate from the Certification Authority used by your organization and get the <KEY> and <CRT> files. Flyte doesn’t manage the lifecycle of certificates so this requirement will need to be managed by your security or infrastructure team. 

[Learn how to import external certificates to ACM](https://docs.aws.amazon.com/acm/latest/userguide/import-certificate-prerequisites.html)

If you're using the CA from ACM, [learn here](https://docs.aws.amazon.com/acm/latest/userguide/gs-acm-request-public.html#request-public-console) how to request a new SSL certificate that will be automatically imported.

In any case, note the generated ARN; it will be used in the custom values file for the Helm chart.
___
Next: Adjust values and upgrade with Helm