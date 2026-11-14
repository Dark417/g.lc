from typing import Annotated

from fastapi import Depends, HTTPException, Request

from app.auth.identity import AuthError, Identity, authenticate
from app.container import Container


def get_container(request: Request) -> Container:
    return request.app.state.container


def get_identity(request: Request) -> Identity:
    try:
        return authenticate(request.headers, request.app.state.container.settings)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


def require_admin(identity: Annotated[Identity, Depends(get_identity)]) -> Identity:
    if not identity.is_admin:
        raise HTTPException(status_code=403, detail="admin role required")
    return identity


ContainerDep = Annotated[Container, Depends(get_container)]
IdentityDep = Annotated[Identity, Depends(get_identity)]
AdminDep = Annotated[Identity, Depends(require_admin)]
