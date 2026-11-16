# 7security — Security From Keys To SSO, Plus Authorization And Tenancy

- **In plain words:** security is a stack. Math gives you keys, keys give you certificates, certificates give you encrypted connections, and on top of those sit logins, tokens and single sign-on, which decide who you are and what you may do.
- Part 0 is new: the protocol stack layer by layer, which uses which, and which frameworks implement it
- Parts B and C moved here from `5reliability-security.md` (threat modeling, identity, authorization, data protection, PKI, multi-tenancy)
- Code for a small auth service in Java, Python and Angular: [7security-c.md](7security-c.md)
- Reliability moved to [5cloud-availability.md](5cloud-availability.md)

## Index

- [0. The Security Stack, Layer By Layer](#l0)
  - [0.1 The stack at a glance](#l0-1)
  - [0.2 Layer 1: cryptographic primitives](#l0-2)
  - [0.3 Layer 2: keys and certificates (PKI)](#l0-3)
  - [0.4 Layer 3: secure transport (TLS, mTLS)](#l0-4)
  - [0.5 Layer 4: proving who you are (authentication)](#l0-5)
  - [0.6 Layer 5: sessions vs tokens (stateful vs stateless)](#l0-6)
  - [0.7 Layer 6: delegation and SSO (OAuth 2.0, OIDC, SAML)](#l0-7)
  - [0.8 Layer 7: authorization (RBAC, ABAC, policies)](#l0-8)
  - [0.9 Protocol vs implementation vs framework vs interface](#l0-9)
  - [0.10 Which uses which](#l0-10)
- [Part B — Security In System Design](#h2)
- [12. Threat Modeling Basics](#s12)
  - [12.1 Three Principles Behind Every Control](#s12-1)
- [13. Identity And Authentication](#s13)
  - [13.1 Users](#s13-1)
  - [13.2 Services](#s13-2)
  - [13.3 Tokens](#s13-3)
- [14. Authorization](#s14)
- [15. Data Protection](#s15)
  - [15.1 Secrets Management](#s15-1)
- [16. Application Security](#s16)
- [17. Network Security](#s17)
- [18. Abuse And Fraud](#s18)
- [19. Audit And Compliance](#s19)
- [20. PKI Essentials](#s20)
- [20b. Identity And Policy Tools](#s20b)
- [20c. Interview Pitfalls](#s20c)
- [Part C — Multi-Tenancy](#h3)
- [21. Isolation Models](#s21)
- [22. Making Pooled Tenancy Safe](#s22)
- [23. Failure Modes](#s23)
- [24. Where This Fits](#s24)

---

<a id="l0"></a>
## 0. The Security Stack, Layer By Layer

- **In plain words:** each layer trusts the one below it. TLS is only as good as the certificate, the certificate only as good as the private key, and OAuth assumes TLS underneath.

<a id="l0-1"></a>
### 0.1 The stack at a glance

```text
 7  Authorization     RBAC / ABAC / ReBAC, policy engines (OPA, Cedar, IAM)
 6  Delegation + SSO  OAuth 2.0 (authorization), OIDC (identity on OAuth), SAML (older SSO)
 5  Session state     server session + cookie (stateful)  vs  JWT access token (stateless)
 4  Authentication    password + hash, MFA (TOTP, WebAuthn / passkeys), client certs, API keys
 3  Secure transport  TLS 1.2 / 1.3, mTLS between services
 2  Keys + identity   key pairs, X.509 certificates, CAs, KMS / HSM
 1  Primitives        hashing, symmetric ciphers, asymmetric crypto, signatures, MACs
```

<a id="l0-2"></a>
### 0.2 Layer 1: cryptographic primitives

| Primitive | In plain words | Examples | Used for |
|---|---|---|---|
| Hash | A one-way fingerprint of data | SHA-256 | Integrity checks, content addressing |
| Password hash | A deliberately slow, salted hash | bcrypt, scrypt, Argon2 | Storing passwords |
| Symmetric cipher | One shared secret key locks and unlocks | AES-GCM | Bulk encryption (data at rest, TLS traffic) |
| Asymmetric crypto | A public key locks, only the private key unlocks | RSA, elliptic curves (ECDHE) | Key exchange, small secrets |
| Signature | Private key signs, anyone with the public key verifies | RSA, ECDSA, Ed25519 | Certificates, JWTs (RS256 / ES256) |
| MAC | A keyed hash only key holders can produce | HMAC-SHA256 | JWT HS256, webhook signatures |

- The catch: never invent crypto or use a plain fast hash (SHA-256) for passwords

<a id="l0-3"></a>
### 0.3 Layer 2: keys and certificates (PKI)

- **Key pair:** a private key you guard and a public key you share
- **X.509 certificate:** "this public key belongs to `api.example.com`", signed by a certificate authority (CA)
- **Chain of trust:** leaf certificate → intermediate CA → root CA preinstalled in browsers and OSes
- **Revocation:** CRL and OCSP; in practice, short-lived certificates beat revocation
- **Key storage:** KMS or an HSM holds master keys; apps use envelope encryption (a data key encrypted by the master key)
- AWS: ACM issues public certificates; ACM Private CA for internal mTLS; KMS for keys

<a id="l0-4"></a>
### 0.4 Layer 3: secure transport (TLS, mTLS)

1. Client says hello with supported ciphers; server replies with its certificate
2. Client validates the chain and the hostname
3. Both run an ECDHE key exchange: a fresh shared secret per connection (forward secrecy)
4. Traffic is encrypted with a symmetric cipher (AES-GCM)

- TLS 1.3 needs one round trip for a new connection (TLS 1.2 needed two)
- **mTLS:** the client also presents a certificate, so both sides are authenticated; common between services (service mesh)
- **Where TLS ends:** at the load balancer or gateway, at a sidecar, or in the app; re-encrypt inside if required

<a id="l0-5"></a>
### 0.5 Layer 4: proving who you are (authentication)

| Method | Who uses it | Catch |
|---|---|---|
| Password + slow hash | End users | Phishing, reuse; add MFA |
| MFA: TOTP, push, WebAuthn / passkeys | End users | Passkeys resist phishing; SMS codes don't |
| API key | Simple machine clients | Long-lived bearer secret; scope it and rotate |
| Client certificate (mTLS) | Services, devices | Certificate lifecycle and rotation |
| Cloud IAM identity (role, workload identity) | Services in the cloud | Best default: no static secrets |

<a id="l0-6"></a>
### 0.6 Layer 5: sessions vs tokens (stateful vs stateless)

- **In plain words:** after login, the server either remembers you (a session it stores) or hands you a signed pass you show each time (a token it doesn't store).

| | Server session + cookie | JWT access token |
|---|---|---|
| State | Stateful: session store (memory, Redis, DB) | Stateless: everything is in the signed token |
| Each request | Look up session id | Verify signature and expiry, no lookup |
| Logout / revoke | Delete the session: instant | Hard: wait for expiry, or keep a denylist (state again) |
| Scaling | Needs a shared store or sticky sessions | Any instance can verify |
| Typical use | Server-rendered web apps, BFF pattern | APIs, mobile, service-to-service |

- Common hybrid: short-lived access JWT (5–15 min) + long-lived refresh token stored server-side and rotated on use
- Browser storage: an `HttpOnly`, `Secure`, `SameSite` cookie resists XSS theft; `localStorage` does not
- 🗣 "Stateless tokens buy horizontal scale and cost instant revocation; I keep access tokens short and refresh tokens revocable."

<a id="l0-7"></a>
### 0.7 Layer 6: delegation and SSO (OAuth 2.0, OIDC, SAML)

- **OAuth 2.0** answers "may this app act for this user?" It issues access tokens; it is not a login protocol by itself
  - Roles: resource owner (user), client (app), authorization server, resource server (API)
  - Flows (grants)
    - Authorization code + PKCE: browsers, mobile, SPAs (the default)
    - Client credentials: service to service, no user
    - Device code: TVs and CLIs
    - Refresh token: get a new access token without a new login
    - Implicit and password grants: deprecated
- **OpenID Connect (OIDC)** adds identity on top of OAuth: an ID token (JWT) saying who logged in, plus a `/userinfo` endpoint and discovery (`/.well-known/openid-configuration`, JWKS)
- **SAML 2.0**: older XML-based SSO, common in enterprise
- **SSO:** log in once at an identity provider (IdP), then reach many apps; built with OIDC or SAML
- IdPs: Okta, Auth0, Microsoft Entra ID, Google, Keycloak (open source), AWS Cognito, Ping

<a id="l0-8"></a>
### 0.8 Layer 7: authorization (RBAC, ABAC, policies)

| Model | In plain words | Example |
|---|---|---|
| RBAC | Permissions attach to roles; users get roles | `ADMIN` can delete orders |
| ABAC | Rules on attributes of user, resource, environment | Only the order's owner, during business hours |
| ReBAC | Permissions follow relationships | Editors of a doc's folder can edit the doc (Google Zanzibar, OpenFGA) |
| Policy engine | Rules written as code, evaluated by a service | OPA / Rego, AWS Cedar, AWS IAM policies |

- Authorize on the server for every request; a hidden button in the UI is not access control
- OAuth scopes describe what a client may do; fine-grained "may this user touch this record" stays in your service

<a id="l0-9"></a>
### 0.9 Protocol vs implementation vs framework vs interface

| Kind | What it is | Examples |
|---|---|---|
| Protocol / standard | The rules on the wire | TLS, OAuth 2.0 (RFC 6749), OIDC, SAML, JWT (RFC 7519), JWK |
| Server implementation | A product that speaks the protocol | Keycloak, Okta, Auth0, Cognito, Spring Authorization Server |
| Library | Code that does one protocol job | Nimbus JOSE + JWT, jjwt (Java); PyJWT, Authlib (Python); OpenSSL |
| Framework integration | Plugs the protocol into a web framework | Spring Security; FastAPI security utilities; Flask-Login; angular-oauth2-oidc |
| Interface / extension point | Where your code plugs in | Spring `SecurityFilterChain`, `UserDetailsService`, `JwtDecoder`; FastAPI `Depends`; Angular `HttpInterceptor`, route guards |

<a id="l0-10"></a>
### 0.10 Which uses which

```text
SSO (OIDC / SAML) --> OAuth 2.0 flows --> JWT (signed with keys from JWKS) --> TLS --> certificates --> key pairs
                                             |
                       resource server verifies signature + issuer + audience + expiry
                                             |
                       authorization (roles / scopes / policies) decides the action
```

- Example request path
  → User logs in at the IdP (OIDC authorization code + PKCE)  
  → The SPA gets an ID token and an access token  
  → The SPA calls the API over TLS with `Authorization: Bearer <access token>`  
  → The API (resource server) fetches the IdP's public keys (JWKS) and verifies the token  
  → The API checks scopes or roles, then the record-level rule  
  → Between services: mTLS or a client-credentials token
- 🗣 "OAuth delegates access, OIDC adds identity, JWTs carry the claims, TLS protects the pipe, and authorization is still my service's job."

---

<a id="h2"></a>
## Part B — Security In System Design

<a id="s12"></a>
## 12. Threat Modeling Basics ★★

- Draw trust boundaries (internet → edge → services → data)
- STRIDE prompts: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege
- For each boundary: who can call it, how they're identified, what they can reach
- 🗣 "At each trust boundary I ask who's calling, how we know, and what they're allowed to touch."

<a id="s12-1"></a>
### 12.1 Three Principles Behind Every Control

- **In plain words:** give each thing as little power as possible, stack several locks, and never trust a caller just because it is inside your network.
- **Least privilege:** every user, service and job gets only the permissions it needs; a compromised component can then reach little
  - Example: the order service's IAM role can write `orders` only, not read `payments`
- **Defense in depth:** several independent layers (WAF, authN, authZ, encryption, audit), so one failure is not a breach
- **Zero trust:** verify every request regardless of network location: mTLS between services, short-lived credentials, per-request authZ
- Catch: least privilege drifts over time; review unused permissions (IAM Access Analyzer, access reviews)

---

<a id="s13"></a>
## 13. Identity And Authentication ★★★

<a id="s13-1"></a>
### 13.1 Users

- OIDC / OAuth2 authorization code flow + PKCE for browser and mobile apps
- MFA for sensitive actions
- Sessions (server-side, cookie) vs tokens (JWT): sessions are easy to revoke; JWTs scale without lookups but need short TTLs

<a id="s13-2"></a>
### 13.2 Services

- mTLS with service certificates; workload identity (SPIFFE IDs, cloud instance principals — OCI "instance principals" / "resource principals")
- No shared static credentials between services

<a id="s13-3"></a>
### 13.3 Tokens

- JWT: header.payload.signature; validate signature, `exp`, `iss`, `aud`
- Short-lived access tokens (minutes) + refresh tokens
- Revocation: short TTL + denylist, or opaque tokens with introspection
- 🗣 "Short-lived JWTs validated locally at each service, refresh tokens for sessions, and mTLS between services."

---

<a id="s14"></a>
## 14. Authorization ★★★

| Model | How | Good for |
|---|---|---|
| RBAC | Roles → permissions | Most apps, admin consoles |
| ABAC | Rules on attributes (tenant, region, tags) | Fine-grained, multi-tenant cloud |
| ReBAC | Relationships (owner, member, shared-with) — Google Zanzibar style | Docs / file sharing |

- Enforce at two levels: coarse at the gateway (scopes), fine in the service (resource ownership)
- Policy engines: OPA, AWS Cedar; cloud IAM policy languages
- OCI IAM example: `Allow group NetworkAdmins to manage virtual-network-family in compartment Prod`
- Watch for the confused-deputy problem: a service acting on behalf of a user must check the **user's** permission, not just its own
- 🗣 "The gateway checks scopes; the service checks this caller can act on this resource in this compartment."

---

<a id="s15"></a>
## 15. Data Protection ★★★

- In transit: TLS 1.2+ (prefer 1.3) at the edge; mTLS internally
- At rest: disk / database encryption; field-level encryption for very sensitive fields
- **Envelope encryption**
  1. KMS holds a master key (often in an HSM, never leaves it)
  2. Service asks KMS for a data key → gets plaintext + encrypted copy
  3. Encrypt the data with the plaintext data key, then discard it
  4. Store the encrypted data key next to the data
  5. To read: ask KMS to decrypt the data key, then decrypt the data
- Key rotation: rotate master keys; re-encrypt data keys, not all data
- Secrets: vault service, short-lived credentials, rotation, never in code or images
- PII: collect less, tokenize (e.g. payment cards), restrict access, set retention
- 🗣 "Envelope encryption: data keys encrypt the data, KMS-held master keys encrypt the data keys, so rotation is cheap."

<a id="s15-1"></a>
### 15.1 Secrets Management

- **In plain words:** passwords and keys that services use should live in one guarded place, be handed out briefly, and change on a schedule, never sit in code.
- Never
  - Hard-code secrets or commit them (even in `.env` files)
  - Put them in command-line arguments (visible in the process list)
  - Bake them into images or plain Kubernetes manifests
- Tools

| Tool | What it adds | Choose when |
|---|---|---|
| AWS Secrets Manager / GCP Secret Manager / OCI Vault | Managed store, versioning, IAM-scoped access, managed rotation for some databases (RDS) | Cloud-native default |
| HashiCorp Vault | Dynamic secrets (DB credentials minted per lease and auto-revoked), PKI for short-lived certificates, encryption as a service | Multi-cloud or on-prem, or you want dynamic credentials |
| Kubernetes Secrets | Base64 in etcd, not encrypted by default | Only with KMS encryption at rest, or synced from a real store via External Secrets Operator / Secrets Store CSI driver |
| AWS SSM Parameter Store | Cheap config + SecureString | Simple config with a few secrets |

- Rotation without downtime: keep two valid versions during the window (Secrets Manager stages `AWSCURRENT` / `AWSPREVIOUS`)
- Audit every secret read; alert on unusual readers
- Best: no secret at all, using workload identity (IAM roles for tasks / pods, instance principals) instead of static keys

---

<a id="s16"></a>
## 16. Application Security ★★

- Injection: parameterized queries, never string-built SQL
- XSS: output encoding, Content Security Policy
- CSRF: SameSite cookies, CSRF tokens
- SSRF: webhooks and URL fetchers must block internal / metadata IPs and use an egress proxy
- Deserialization: don't deserialize untrusted data into arbitrary types
- Dependencies: scanning, pinning, SBOM
- Webhooks in and out: HMAC signatures + timestamps ([3messaging.md](3messaging.md) section 7.6)
- **IDOR (insecure direct object reference):** `/api/orders/123` with someone else's ID; always check the caller owns or may see the resource, never trust the ID alone
- Command injection: never pass user input to a shell; NoSQL injection: no `$where` or operator objects built from raw input
- Broken authentication: rate-limit and lock out login, hash passwords with Argon2id / bcrypt / scrypt (never fast hashes like SHA-256 or MD5), offer MFA
- Browser transport: HSTS so browsers only use HTTPS; certificate pinning only for mobile apps you control (pinning breaks on rotation if done carelessly)
- Reference lists: OWASP Top 10 (web risks), OWASP API Security Top 10, OWASP ASVS (verification checklist)

---

<a id="s17"></a>
## 17. Network Security ★★

- Private networks (VPC / VCN), public subnets only for edge components
- Security groups / network security groups / security lists: least-privilege ports
- Private endpoints to managed services (no internet path)
- Zero trust: authenticate and authorize every call, even inside the network
- WAF for common web attacks; DDoS protection at the edge (anycast, scrubbing)
- Egress control: allowlists for outbound calls

---

<a id="s18"></a>
## 18. Abuse And Fraud ★

- Rate limits per user / IP / tenant; stricter on login, signup, payments
- Bot detection, CAPTCHA on suspicious traffic
- Account takeover defenses: MFA, anomaly detection, breached-password checks
- Business abuse: fake listings, promo abuse → risk scoring, manual review queues

---

<a id="s19"></a>
## 19. Audit And Compliance ★

- **In plain words:** an audit log answers "who did what, to which record, when, and did it work", in a form nobody can quietly edit.
- What to log: login success and failure, authorization denials, every change to sensitive data, admin actions (role and config changes)
- Requirements: append-only and tamper-evident (S3 Object Lock / WORM storage, hash chaining), structured and indexed by actor, resource and time, retained for the period the regime requires (often years)
- Keep it separate from debug logs: different access, retention and no sampling
```json
{"event_id": "evt-9f2", "ts": "2026-07-01T15:30:00Z",
 "actor": {"user_id": "u-123", "ip": "203.0.113.7"},
 "action": "DELETE", "resource": {"type": "payment", "id": "p-456"},
 "outcome": "SUCCESS", "service": "payment-service", "request_id": "req-789"}
```
- Common regimes to name
  - PCI DSS (payment cards): tokenize, keep card data out of most systems
  - HIPAA (health data, e.g. Oracle Health): access logging, encryption, minimum necessary access
  - SOC 2: controls over security and availability
  - GDPR / data residency: deletion, regional storage
- 🗣 "Card data never touches our services; the payment provider tokenizes it, which shrinks PCI scope."

---

<a id="s20"></a>
## 20. PKI Essentials ★★

- Relevant for OCI infra roles (PKI, certificates, service identity)
- CA hierarchy: offline root CA → intermediate CAs → leaf certificates
- Issuance: CSR → validation → signed certificate; automate (ACME-style)
- Short-lived certificates reduce reliance on revocation
- Revocation: CRL (published list) or OCSP (online status, OCSP stapling)
- Rotation: overlap old and new (trust bundles include both during rollover)
- Keys for CAs in HSMs; strict audit on signing
- 🗣 "Short-lived leaf certs from an intermediate CA, root kept offline, and trust bundles carry old and new during rollover."

---

<a id="s20b"></a>
## 20b. Identity And Policy Tools ★★

| Tool | What it is | Choose when |
|---|---|---|
| Keycloak | Open-source identity provider: SSO, OIDC, SAML, LDAP / AD | Self-hosted IdP |
| Auth0 / Okta / Entra ID / Cognito | Managed identity: SSO, MFA, social login, SCIM provisioning | Buy over build for user identity |
| Cloud IAM (AWS IAM, OCI IAM, GCP IAM) | Who can touch which cloud resource | Always, for infrastructure |
| OPA (Rego) / AWS Cedar | Policy engines; decouple authZ rules from code | Many services sharing complex rules; Kubernetes admission |
| Zanzibar-style (OpenFGA, SpiceDB, Ory Keto) | Relationship-based authZ at scale | Sharing models like Google Drive |

<a id="s20c"></a>
## 20c. Interview Pitfalls ★★

- Hashing passwords with SHA-256 or MD5: fast hashes are brute-forceable; use Argon2id or bcrypt
- Covering authN but not authZ: "users log in with JWT" says nothing about what they may access
- No revocation story for JWTs: short TTL + refresh, plus a denylist for high-risk actions
- Permissions baked into long-lived JWT claims go stale after a role change
- No rate limit on login and password reset
- "Internal traffic doesn't need TLS": wrong under zero trust

<a id="h3"></a>
## Part C — Multi-Tenancy

<a id="s21"></a>
## 21. Isolation Models ★★★

| Model | How | Good | Cost | Choose when |
|---|---|---|---|---|
| Silo | Dedicated stack / DB per tenant | Strong isolation, per-tenant tuning | Expensive, many deployments | Regulated or very large tenants |
| Pool | Shared stack; tenant_id in every row / key | Efficient, simple ops | Noisy neighbors, authZ must be perfect | Many small tenants (default) |
| Bridge / cell | Groups of tenants per cell | Balance | Placement and migration logic | Mixed tenant sizes at scale |

<a id="s22"></a>
## 22. Making Pooled Tenancy Safe ★★★

- **Tenant context** propagated on every request (from the token, never from a client-supplied header)
- **Tenant id in every key and query**
  - Partition keys start with tenant id
  - Postgres row-level security as a second guard
- **Per-tenant quotas and rate limits** at the gateway and in queues
- **Fair scheduling**: per-tenant queues or weighted fair queuing so one tenant's burst doesn't starve others
- **Shuffle sharding** of workers (section 7)
- **Per-tenant encryption keys** (optional): customer-managed keys
- **Per-tenant observability and metering**: usage for billing, top-N tenant dashboards
- **Tenant placement and migration**: move hot tenants to bigger / dedicated cells
- 🗣 "Tenant id comes from the token, prefixes every key, and every queue and rate limit is per tenant, so one tenant can't starve the rest."

---

<a id="s23"></a>
## 23. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Noisy neighbor | One tenant's burst | Per-tenant latency / usage spikes | Quotas, fair queuing, shuffle sharding, cell move |
| Cross-tenant data leak | Missing tenant filter | Audit / bug report | Tenant id in keys, row-level security, tests |
| Token theft | Long-lived token leaked | Unusual usage | Short TTLs, binding, revocation |
| SSRF via webhook | User-supplied URL hits metadata service | Security scan | Egress proxy, IP blocklists |
| Key compromise | Leaked secret | Alerts, audit | Rotation, vault, short-lived credentials |

---

<a id="s24"></a>
## 24. Where This Fits

- Place: the deep doc behind 1sd.md section 8.4; code in [7security-c.md](7security-c.md)
- Time: 1–2 days; most valuable for Oracle OCI (PKI team) and any role that asks about auth
- I should be able to
  - Walk the stack from key pair to SSO and say what each layer adds
  - Explain sessions vs JWTs, and how to revoke a JWT
  - Explain OAuth 2.0 code + PKCE and client credentials, and what OIDC adds
  - Explain envelope encryption, JWT validation and the silo / pool / cell tradeoff in one breath each
