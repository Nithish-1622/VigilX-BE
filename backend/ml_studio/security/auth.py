from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from fastapi import HTTPException, Request, status


@dataclass(frozen=True)
class Identity:
    user_id: str
    username: str
    permissions: frozenset[str]
    tenant_id: str


def _parse_permissions(raw: str | None) -> frozenset[str]:
    if not raw:
        return frozenset()
    parts: list[str] = []
    for chunk in raw.replace(";", ",").split(","):
        p = chunk.strip()
        if p:
            parts.append(p)
    return frozenset(parts)


def get_current_identity(request: Request) -> Identity:
    user_id = (request.headers.get("X-User-ID") or "").strip()
    username = (request.headers.get("X-Username") or "").strip()
    perms_raw = request.headers.get("X-Permissions")
    tenant_id = (request.headers.get("X-Tenant-ID") or "default").strip() or "default"

    return Identity(
        user_id=user_id or "anonymous",
        username=username or "anonymous",
        permissions=_parse_permissions(perms_raw),
        tenant_id=tenant_id,
    )


def get_current_tenant_id(request: Request) -> str:
    return (request.headers.get("X-Tenant-ID") or "default").strip() or "default"


def require_permission(permission: str) -> Callable[[Request], Identity]:
    def _dep(request: Request) -> Identity:
        ident = get_current_identity(request)
        if permission not in ident.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission}",
            )
        return ident

    return _dep
