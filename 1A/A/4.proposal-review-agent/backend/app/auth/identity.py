"""Who is calling, and are they an admin. See docs/design/06-security.md.

- ServiceTokenAuth (always on): X-Service-Token in SERVICE_TOKENS -> service identity, role user.
- DevHeaderAuth (AUTH_MODE=dev): trusts X-User-Email. ILLUSTRATION: anyone can be anyone.
- IapAuth (AUTH_MODE=iap): verifies Google IAP's signed JWT. The email comes from the verified
  token, never from a plain header.
Roles are decided server-side from ADMIN_USERS. The client never sends a role.
"""

from dataclasses import dataclass
from typing import Literal

from app.config import Settings

IAP_CERTS = "https://www.gstatic.com/iap/verify/public_key"
IAP_ISSUER = "https://cloud.google.com/iap"
Role = Literal["admin", "user"]


class AuthError(Exception):
    pass


@dataclass(frozen=True)
class Identity:
    user_id: str
    role: Role
    kind: Literal["human", "service"] = "human"

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


def role_for(user_id: str, settings: Settings) -> Role:
    return "admin" if user_id.lower() in settings.admins else "user"


_request = None


def verify_iap_jwt(assertion: str, audience: str) -> str:
    """Return the verified email. PRODUCTION: cache the certs (google-auth fetches per call)."""
    global _request
    from google.auth.transport import requests as ga_requests
    from google.oauth2 import id_token

    if not assertion:
        raise AuthError("missing IAP assertion")
    _request = _request or ga_requests.Request()
    try:
        claims = id_token.verify_token(assertion, _request, audience=audience, certs_url=IAP_CERTS)
    except ValueError as e:
        raise AuthError(f"invalid IAP assertion: {e}") from e
    if claims.get("iss") != IAP_ISSUER or not claims.get("email"):
        raise AuthError("unexpected IAP token claims")
    return claims["email"]


def authenticate(headers, settings: Settings) -> Identity:
    token = headers.get("x-service-token")
    if token:
        if token not in settings.service_token_set:
            raise AuthError("invalid service token")
        return Identity(user_id="svc:mcp", role="user", kind="service")

    if settings.auth_mode == "iap":
        email = verify_iap_jwt(headers.get("x-goog-iap-jwt-assertion", ""), settings.iap_audience)
    else:
        email = headers.get("x-user-email") or settings.dev_default_user
    email = email.strip().lower()
    if not email or len(email) > 200:
        raise AuthError("missing identity")
    return Identity(user_id=email, role=role_for(email, settings))
