"""Roles, permissions, and the authenticated Principal (SC-1).

Permissions are the atomic capabilities endpoints check; roles bundle them. A Principal
is whatever the resolver produced from a credential — it always carries a tenant_id, so
every downstream store call is tenant-scoped.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class Permission(str, Enum):
    DECISION_CREATE = "decision:create"
    DECISION_READ = "decision:read"
    DECISION_LIST = "decision:list"
    OUTCOME_WRITE = "outcome:write"
    REVIEW_ACT = "review:act"
    AUDIT_VERIFY = "audit:verify"
    ADMIN = "admin"


class Role(str, Enum):
    VIEWER = "viewer"
    REQUESTER = "requester"
    REVIEWER = "reviewer"
    ADMIN = "admin"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.VIEWER: {Permission.DECISION_READ, Permission.DECISION_LIST},
    Role.REQUESTER: {
        Permission.DECISION_READ,
        Permission.DECISION_LIST,
        Permission.DECISION_CREATE,
        Permission.OUTCOME_WRITE,
    },
    Role.REVIEWER: {
        Permission.DECISION_READ,
        Permission.DECISION_LIST,
        Permission.REVIEW_ACT,
        Permission.AUDIT_VERIFY,
    },
    Role.ADMIN: set(Permission),
}


class Principal(BaseModel):
    """The authenticated caller. Produced by the credential resolver, consumed by deps."""

    tenant_id: str
    subject: str
    roles: list[Role]

    @property
    def permissions(self) -> set[Permission]:
        perms: set[Permission] = set()
        for role in self.roles:
            perms |= ROLE_PERMISSIONS.get(role, set())
        return perms

    def can(self, permission: Permission) -> bool:
        return permission in self.permissions
