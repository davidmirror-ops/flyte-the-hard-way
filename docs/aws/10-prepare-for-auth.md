# Prepare your environment for auth

In this guide, you'll complete the steps to enable and configure auth (both authentication and authorization) for Flyte **using Okta both as IdP and external authorization server**.
Further explanations and instructions for other IdPs can be found in the [Flyte documentation](https://docs.flyte.org/en/latest/deployment/configuration/auth_setup.html)

A heavily summarized description of the auth implementation in Flyte and how it operates with an External Authorization Server is presented in the following diagram:

![](./images/flyte-auth-v3.png)

## Glossary

Before heading to the steps, below you'll find brief definitions for some terms we're going to use:

- Flow: the set of steps a component will follow to perform a task in a secure manner
- IdP (Identity Provider): a component external to Flyte that will provide user identity. Potentially, it will also be used by Flyte to redirect authorization requests
- Application: your Flyte deployment to be registered in one of the [supported IdPs](https://docs.flyte.org/en/latest/deployment/configuration/auth_setup.html#identity-providers-support)

Regardless of the IdP you choose, Flyte uses the OAuth 2.0 protocol to handle Authorization and OIDC for Identity Management. If you want to dive a little deeper, you can check Okta's [Illustrated Guide to OAuth and OIDC](https://developer.okta.com/blog/2019/10/21/illustrated-guide-to-oauth-and-oidc).

## Create app integrations

In this section you'll create three app integrations, one for each component that is part of an authentication/authorization flow: `flyteconsole`, `flytectl` and `flytepropeller`:

### flyteconsole

1. Login to your Okta account (you can [sign up for a new one](https://developer.okta.com/signup/))
2. Create a new **App integration**
3. Select `OIDC - OpenID Connect`
4. Select `Web Application` as the **Application type**
5. Use `flyteconsole` as the **App integration name**
6. Replace the default **Sign-in redirect URIs** with your Ingress DNS name adding `/callback` at the end.

> Example: `https://flyte-the-hard-way.uniondemo.run/callback`

7. Use the same value as the **Sign-out redirect URIs**
8. Select `Allow everyone in your organization to access` in the **Controlled access** section. You can adapt this setting to reflect your organization's security policies and groups assignments.
9. Click **Save**
10. Take note of the `Client ID` and `Client secret`

### flytectl

11. Create a new **App integration**
12. Select `OIDC - OpenID Connect`
13. Select `Native Application` as the **Application type**
14. Use `flytectl` as the **App integration name**
15. Add `http://localhost:53593/callback` to the sign-in redirect URIs. The other options can remain as default.
16. Consult with your security team regarding the specific groups that should have access to Flyte's command line tools (like `flytectl` or `pyflyte`) and configure the **Assignments** section accordingly
17. Click **Save**
18. Take note of the `ClientID`. There will not be a client secret

### flytepropeller

19. Create a new App integration
20. Select `OIDC - OpenID Connect`
21. Select `Web Application` as the **Application type**
22. Check the `Client credentials` option in the **Client acting on behalf of itself** section
23. As this is not a user-facing app, it does not need a specific redirect URI nor it needs to be assigned to any user/group
24. Click **Save**
25. Take note of the `ClientID` and `ClientSecret`

## Configure an authorization server

25. From the Okta dashboard, go the **Security** option in the lefthand side menu
26. Select **API**
27. Click on **Add Authorization Server**
28. Set a descriptive **Name**
29. Set the **Audience** parameter to match exactly the domain name of your Ingress resource.

> Example: `https://flyte-the-hard-way.uniondemo.run` (see [Lab 9](09-connect-Flyte-ingress.md) for more details)

30. Click **Save**
31. Inside the Authorization Server config menu, go to **Scopes**
32. Click **Add Scope**
33. Set the name to `all`
34. Check the `Required` option in the **User consent** section
35. Uncheck the `Block services from requesting this scope` option. Otherwise it would block inter-service requests, necessary for both user and non-user facing Flyte components
36. Click **Save**
37. Add another scope with the following parameters:

- Name: `offline`
- **User consent** : `Required`
- Uncheck `Block services from requesting this scope`
- **Metadata**: `Include in public metadata`

38. Now go to the **Access policies** tab inside the authorization server configuration page
39. Click **Add Policy**
40. Set a name and leave the **Assign to** option by default
41. Add an informative **Description**
42. Click on **Create Policy**
43. Click on **Add Rule**
44. Set a **Rule Name** and leave all the other options by default unless otherwise indicated by your organization's security policies
45. Click on **Create Rule**
46. At the top of the page, click on **Back to Authorization Servers**
47. Take note of the **Issuer URI** for your Authorization Server. It will be used as the `baseURL` parameter in the Helm chart.

---

Next: [upgrade your Helm release to use auth](11-upgrade-with-auth.md)
