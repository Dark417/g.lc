# 7security-c — A Small Auth Service In Java, Python And Angular

- **In plain words:** one tiny auth system built three ways: a login endpoint that checks a password and hands out a signed token, an API that checks that token on every call, and a front end that attaches the token and hides pages you can't use.
- `-c` = code file; the concepts are in [7security.md](7security.md) (the stack, sessions vs tokens, OAuth / OIDC)
- Teaching version: in production, let an identity provider (Keycloak, Cognito, Okta, Entra ID) or Spring Authorization Server issue tokens; your services only validate them

## Index

- [0. One-Minute Version](#0-one-minute-version)
- [1. What We Build](#1-what-we-build)
- [2. Java: Spring Boot + Spring Security](#2-java-spring-boot--spring-security)
  - [2.1 Issuing tokens (the auth service)](#21-issuing-tokens-the-auth-service)
  - [2.2 Validating tokens (the resource server)](#22-validating-tokens-the-resource-server)
  - [2.3 Authorization: roles, scopes, ownership](#23-authorization-roles-scopes-ownership)
- [3. Python: FastAPI](#3-python-fastapi)
- [4. Python: Flask (session-based, stateful)](#4-python-flask-session-based-stateful)
- [5. Angular: Attaching Tokens And Guarding Routes](#5-angular-attaching-tokens-and-guarding-routes)
- [6. Refresh Tokens And Logout](#6-refresh-tokens-and-logout)
- [7. How Each Framework Plugs In](#7-how-each-framework-plugs-in)
- [8. Checklist](#8-checklist)
- [9. Failure Modes](#9-failure-modes)
- [References](#references)

---

## 0. One-Minute Version

- **Login:** verify password hash → issue a short-lived signed access token (JWT, RS256) + a refresh token
- **Every API call:** verify signature, issuer, audience, expiry → build the user's identity → check roles or scopes → check the record belongs to the user
- **Front end:** get tokens via OIDC code + PKCE (or a backend-for-frontend session cookie), attach `Authorization: Bearer`, guard routes for UX only
- **Catch:** the server must authorize every request; a hidden Angular route is not security
- 🗣 "The auth server signs with a private key, every API verifies with the public key from JWKS, and authorization is checked on the server per request and per record."

## 1. What We Build

```text
Angular SPA --(username/password or OIDC redirect)--> Auth service  --issues--> access JWT (15 min) + refresh token
     |                                                    |
     +--(Bearer access JWT)--> Orders API (resource server) <--(JWKS public key)--+
                                  checks: signature, iss, aud, exp -> roles/scopes -> owner of the order
```

- Claims in the access token: `sub` (user id), `iss`, `aud`, `exp`, `iat`, `scope` (`orders:read orders:write`), `roles` (`USER`, `ADMIN`)

## 2. Java: Spring Boot + Spring Security

- **In plain words:** Spring Security is a chain of filters in front of your controllers; one filter reads the token, builds the user, and later checks decide what that user may do.
- Dependencies: `spring-boot-starter-security`, `spring-boot-starter-oauth2-resource-server` (brings Nimbus JOSE + JWT)

### 2.1 Issuing tokens (the auth service)

```java
@Configuration
class AuthConfig {
    @Bean PasswordEncoder passwordEncoder() {               // bcrypt by default, upgradable
        return PasswordEncoderFactories.createDelegatingPasswordEncoder();
    }
    @Bean RSAKey rsaKey() throws JOSEException {              // load from KMS / secrets in production
        return new RSAKeyGenerator(2048).keyID("k1").generate();
    }
    @Bean JwtEncoder jwtEncoder(RSAKey key) {
        return new NimbusJwtEncoder(new ImmutableJWKSet<>(new JWKSet(key)));
    }
    @Bean AuthenticationManager authManager(UserDetailsService users, PasswordEncoder enc) {
        var provider = new DaoAuthenticationProvider(enc);  // Spring Security 6.3+ constructor
        provider.setUserDetailsService(users);
        return new ProviderManager(provider);
    }
}

@RestController
class TokenController {
    private final AuthenticationManager auth; private final JwtEncoder jwt;
    TokenController(AuthenticationManager auth, JwtEncoder jwt) { this.auth = auth; this.jwt = jwt; }

    @PostMapping("/token")
    Map<String, String> token(@RequestBody Login req) {
        Authentication a = auth.authenticate(                       // checks bcrypt hash
            UsernamePasswordAuthenticationToken.unauthenticated(req.username(), req.password()));
        Instant now = Instant.now();
        JwtClaimsSet claims = JwtClaimsSet.builder()
            .issuer("https://auth.example.com").audience(List.of("orders-api"))
            .subject(a.getName()).issuedAt(now).expiresAt(now.plus(15, ChronoUnit.MINUTES))
            .claim("roles", a.getAuthorities().stream().map(GrantedAuthority::getAuthority).toList())
            .claim("scope", "orders:read orders:write")
            .build();
        String token = jwt.encode(JwtEncoderParameters.from(
            JwsHeader.with(SignatureAlgorithm.RS256).keyId("k1").build(), claims)).getTokenValue();
        return Map.of("access_token", token, "token_type", "Bearer");
    }

    @GetMapping("/.well-known/jwks.json")                       // public keys for resource servers
    Map<String, Object> jwks(RSAKey key) { return new JWKSet(key.toPublicJWK()).toJSONObject(); }
}
record Login(String username, String password) {}
```

- `UserDetailsService` loads the user and hashed password from your DB (Spring Data repository)
- Login endpoint must be rate-limited and must return the same error for "no such user" and "wrong password"

### 2.2 Validating tokens (the resource server)

```java
@Configuration
@EnableMethodSecurity                                         // enables @PreAuthorize
class ApiSecurity {
    @Bean SecurityFilterChain api(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())                     // bearer tokens in headers: no cookie, no CSRF risk
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(a -> a
                .requestMatchers("/actuator/health").permitAll()
                .requestMatchers(HttpMethod.GET, "/orders/**").hasAuthority("SCOPE_orders:read")
                .anyRequest().authenticated())
            .oauth2ResourceServer(o -> o.jwt(j -> j.jwtAuthenticationConverter(rolesConverter())))
            .build();
    }
    // map the "roles" claim to ROLE_* authorities (the "scope" claim maps to SCOPE_* by default)
    JwtAuthenticationConverter rolesConverter() {
        var roles = new JwtGrantedAuthoritiesConverter();
        roles.setAuthoritiesClaimName("roles"); roles.setAuthorityPrefix("ROLE_");
        var scopes = new JwtGrantedAuthoritiesConverter();
        var conv = new JwtAuthenticationConverter();
        conv.setJwtGrantedAuthoritiesConverter(jwt -> {
            var all = new ArrayList<GrantedAuthority>(scopes.convert(jwt));
            all.addAll(roles.convert(jwt));
            return all;
        });
        return conv;
    }
}
```

```yaml
# application.yml of the Orders API
spring.security.oauth2.resourceserver.jwt:
  issuer-uri: https://auth.example.com          # discovers JWKS, checks "iss"
  audiences: orders-api                         # checks "aud" (Spring Boot 3.2+)
```

- Spring fetches and caches the JWKS, verifies the signature and `exp` / `nbf` / `iss` / `aud` on every request, no DB call

### 2.3 Authorization: roles, scopes, ownership

```java
@Service
class OrderService {
    @PreAuthorize("hasRole('ADMIN') or hasAuthority('SCOPE_orders:write')")
    public Order cancel(long orderId, @AuthenticationPrincipal Jwt jwt) {
        Order o = repo.findById(orderId).orElseThrow();
        if (!o.ownerId().equals(jwt.getSubject()) && !hasRole(jwt, "ADMIN"))
            throw new AccessDeniedException("not your order");      // record-level check → 403
        return o.cancel();
    }
}
```

- Three levels: authenticated at all → coarse permission (role / scope) → this specific record

## 3. Python: FastAPI

- **In plain words:** FastAPI has no security filter chain; you write small dependency functions that read the token and return the user, and each endpoint asks for them.
- Libraries: `PyJWT[crypto]` for JWT, `pwdlib` or `bcrypt` for hashing (passlib is no longer maintained); Authlib for full OAuth / OIDC clients

```python
from datetime import datetime, timedelta, timezone
import jwt                                            # PyJWT
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash

app = FastAPI()
hasher = PasswordHash.recommended()                   # Argon2
oauth2 = OAuth2PasswordBearer(tokenUrl="token")
PRIVATE_KEY, PUBLIC_KEY = load_keys()                 # from a secrets manager, never in code
ISS, AUD = "https://auth.example.com", "orders-api"

@app.post("/token")
def token(form: OAuth2PasswordRequestForm = Depends()) -> dict:
    user = users.get(form.username)
    if not user or not hasher.verify(form.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")
    now = datetime.now(timezone.utc)
    claims = {"sub": user.id, "iss": ISS, "aud": AUD, "iat": now,
              "exp": now + timedelta(minutes=15), "roles": user.roles}
    return {"access_token": jwt.encode(claims, PRIVATE_KEY, algorithm="RS256"), "token_type": "bearer"}

def current_user(token: str = Depends(oauth2)) -> dict:
    try:
        return jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"], audience=AUD, issuer=ISS)
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token",
                            headers={"WWW-Authenticate": "Bearer"})

def require_role(role: str):
    def check(user: dict = Depends(current_user)) -> dict:
        if role not in user.get("roles", []):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "forbidden")
        return user
    return check

@app.post("/orders/{order_id}/cancel")
def cancel(order_id: str, user: dict = Depends(current_user)) -> dict:
    order = orders.get(order_id)
    if order.owner_id != user["sub"] and "ADMIN" not in user["roles"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "not your order")
    return order.cancel()

@app.delete("/admin/users/{uid}", dependencies=[Depends(require_role("ADMIN"))])
def delete_user(uid: str) -> None: ...
```

- Always pass `algorithms=[...]` to `jwt.decode`: never let the token header pick the algorithm
- To validate tokens from an IdP, fetch its keys with `jwt.PyJWKClient(jwks_url)`

## 4. Python: Flask (session-based, stateful)

- **In plain words:** this version keeps the login on the server: Flask stores a session and the browser holds only a cookie, the classic stateful model.

```python
from flask import Flask, abort, request
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

app = Flask(__name__)
app.config.update(SECRET_KEY=load_secret(), SESSION_COOKIE_HTTPONLY=True,
                  SESSION_COOKIE_SECURE=True, SESSION_COOKIE_SAMESITE="Lax")
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id: str): return users.by_id(user_id)

@app.post("/login")
def login():
    user = users.by_name(request.form["username"])
    if not user or not hasher.verify(request.form["password"], user.password_hash):
        abort(401)
    login_user(user)                                  # session cookie set
    return {"ok": True}

@app.post("/logout")
@login_required
def logout():
    logout_user(); return {"ok": True}                # instant revocation: the session is gone

@app.get("/orders")
@login_required
def my_orders(): return orders.for_owner(current_user.id)
```

- Flask's default session is a signed cookie; for server-side storage (revocable, larger) use Flask-Session with Redis
- Cookie sessions need CSRF protection (Flask-WTF `CSRFProtect`) for state-changing requests
- Token-based Flask: Flask-JWT-Extended gives the same model as section 3

## 5. Angular: Attaching Tokens And Guarding Routes

- **In plain words:** the front end adds the token to every API call and hides pages the user can't use, but the real checks happen on the server.

```typescript
// auth.interceptor.ts — attach the access token to API calls
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const token = auth.accessToken();                   // kept in memory, not localStorage
  if (!token || !req.url.startsWith(environment.apiUrl)) return next(req);
  return next(req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })).pipe(
    catchError(err => err.status === 401
      ? auth.refresh().pipe(switchMap(t => next(req.clone({ setHeaders: { Authorization: `Bearer ${t}` } }))))
      : throwError(() => err)));
};

// admin.guard.ts — hide routes the user can't use (UX only)
export const adminGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  return auth.hasRole('ADMIN') ? true : inject(Router).createUrlTree(['/forbidden']);
};

// app.config.ts
export const appConfig: ApplicationConfig = {
  providers: [provideHttpClient(withInterceptors([authInterceptor])),
              provideRouter([{ path: 'admin', component: AdminPage, canActivate: [adminGuard] }])],
};
```

- Getting tokens the right way: OIDC authorization code + PKCE with a library (angular-oauth2-oidc, angular-auth-oidc-client), never a password form talking to `/token` in a public SPA
- Storage: memory beats `localStorage` (XSS can read storage); best is a **BFF**: the backend holds tokens and the browser gets an `HttpOnly` session cookie
- Angular escapes template output by default; don't bypass it with `bypassSecurityTrustHtml` on user data

## 6. Refresh Tokens And Logout

- **In plain words:** the access token is short so a stolen one dies fast; the refresh token is long-lived but stored and checked on the server, so it can be revoked.
- Issue a random opaque refresh token; store only its hash with user id, expiry and a family id
- On refresh: verify, issue a new access token **and a new refresh token**, invalidate the old one (rotation)
- Reuse of an old refresh token = theft signal → revoke the whole family
- Logout: delete the refresh token server-side; the access token expires within minutes (or add its `jti` to a short denylist in Redis)
- Deliver refresh tokens in an `HttpOnly`, `Secure`, `SameSite=Strict` cookie scoped to the refresh path

## 7. How Each Framework Plugs In

| | Spring Security (Java) | FastAPI (Python) | Flask (Python) | Angular (TypeScript) |
|---|---|---|---|---|
| Where auth runs | Servlet filter chain before controllers | Dependencies (`Depends`) per endpoint | Decorators + extensions | Client side only (UX) |
| Extension points | `SecurityFilterChain`, `UserDetailsService`, `JwtDecoder`, `AuthenticationProvider` | `OAuth2PasswordBearer`, `HTTPBearer`, custom dependencies | `LoginManager.user_loader`, `@login_required` | `HttpInterceptorFn`, `CanActivateFn` guards |
| Token validation | `oauth2ResourceServer().jwt()` with JWKS | PyJWT / Authlib in a dependency | Flask-JWT-Extended | n/a (server's job) |
| Sessions | `SessionCreationPolicy`, Spring Session (Redis) | Usually stateless tokens | Signed cookie or Flask-Session | Holds tokens or relies on BFF cookie |
| Authorization | `authorizeHttpRequests`, `@PreAuthorize` | Role-check dependencies | Custom decorators, Flask-Principal | Route guards, hide UI elements |
| OIDC login | `oauth2Login()` | Authlib | Authlib | angular-oauth2-oidc |

## 8. Checklist

- Passwords: bcrypt / Argon2 via the framework encoder → prevents cracked hashes after a leak
- Asymmetric signing (RS256 / ES256) with key rotation (`kid`) → services verify without holding the signing key
- Validate `iss`, `aud`, `exp`, algorithm → prevents token confusion and `alg=none` attacks
- Short access tokens, rotated refresh tokens → limits stolen-token damage
- Server-side authorization per request and per record → a hidden button is not access control
- Rate-limit and lock out login attempts → slows credential stuffing
- TLS everywhere; `HttpOnly`, `Secure`, `SameSite` cookies → prevents token theft in transit and via XSS
- Never log tokens or passwords

## 9. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Algorithm confusion | Decoder trusts the token's `alg` header | Pentest finding | Pin allowed algorithms |
| Token accepted by the wrong API | No `aud` check | Tokens for service A work on B | Validate audience |
| Can't log users out | Long-lived JWT, no refresh store | Users keep access after logout or disable | Short TTL + revocable refresh tokens, denylist |
| IDOR (insecure direct object reference) | Only role checks, no ownership check | User reads another user's order by id | Record-level checks |
| Token theft via XSS | Tokens in `localStorage` | Unusual sessions | Memory or BFF + `HttpOnly` cookie, CSP |
| CSRF on cookie auth | Cookie sessions without CSRF tokens | Forged requests | CSRF tokens, `SameSite` cookies |

## References

- [Spring Security reference — OAuth 2.0 Resource Server JWT](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html)
- [FastAPI docs — Security: OAuth2 with password and JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Flask-Login documentation](https://flask-login.readthedocs.io/)
- [Angular docs — HTTP interceptors](https://angular.dev/guide/http/interceptors) and [Security](https://angular.dev/best-practices/security)
- [OAuth 2.0 for Browser-Based Apps (IETF draft)](https://datatracker.ietf.org/doc/draft-ietf-oauth-browser-based-apps/)
- [OWASP JWT Cheat Sheet for Java](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
