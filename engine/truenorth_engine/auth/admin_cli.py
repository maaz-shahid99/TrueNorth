"""Admin CLI for API-key management (SC-1).

    truenorth-admin mint --tenant acme --subject alice@acme --role requester --role reviewer
    truenorth-admin list --tenant acme
    truenorth-admin revoke --id <key-id> --tenant acme

The minted key is printed once and is not recoverable afterwards.
"""

from __future__ import annotations

import argparse
import sys

from ..config import get_settings
from .keys import get_keystore
from .rbac import Role

_ROLE_CHOICES = [r.value for r in Role]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="truenorth-admin", description="Manage TrueNorth API keys."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    mint_p = sub.add_parser("mint", help="Create a new API key.")
    mint_p.add_argument("--tenant", default="default")
    mint_p.add_argument("--subject", required=True, help="User or service identifier.")
    mint_p.add_argument(
        "--role", action="append", required=True, choices=_ROLE_CHOICES, dest="roles"
    )

    list_p = sub.add_parser("list", help="List API keys for a tenant.")
    list_p.add_argument("--tenant", default="default")

    revoke_p = sub.add_parser("revoke", help="Revoke an API key by id.")
    revoke_p.add_argument("--id", required=True, dest="key_id")
    revoke_p.add_argument("--tenant", default="default")

    args = parser.parse_args(argv)
    keystore = get_keystore(get_settings())

    if args.cmd == "mint":
        key, info = keystore.mint(args.tenant, args.subject, [Role(r) for r in args.roles])
        print("API key (store it now — it is not recoverable):")
        print(f"  {key}")
        print(
            f"id={info.id} tenant={info.tenant_id} subject={info.subject} "
            f"roles={[r.value for r in info.roles]}"
        )
    elif args.cmd == "list":
        for info in keystore.list(args.tenant):
            roles = ",".join(r.value for r in info.roles)
            print(f"{info.id}  {info.subject:24}  roles={roles:30}  active={info.active}")
    elif args.cmd == "revoke":
        print("revoked" if keystore.revoke(args.key_id, args.tenant) else "not found")

    return 0


if __name__ == "__main__":
    sys.exit(main())
