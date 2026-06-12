"""Authentication, multi-tenancy, and RBAC (SC-1).

API-key based to start, behind a resolver seam (`KeyStore.resolve` -> `Principal`) that a
JWT/OIDC verifier can drop into later without touching the endpoints. Kept import-light
so the persistence layer can register the api_keys table without an import cycle.
"""
