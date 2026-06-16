import { KeysManager } from "@/components/settings/KeysManager";
import { getKeys } from "@/lib/data";

export default async function MembersPage() {
  const keys = await getKeys();
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Members & API keys</h1>
        <p className="text-sm text-muted">
          Per-tenant API keys and roles. Admin-only; managed by the engine KeyStore.
        </p>
      </div>
      <KeysManager initialKeys={keys} />
    </div>
  );
}
