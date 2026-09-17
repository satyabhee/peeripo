import { getPendingAura } from "@/lib/api";
import ReviewButtons from "./review-buttons";

export default async function AuraAdminPage() {
  const pending = await getPendingAura();

  return (
    <main style={{ padding: 24 }}>
      <h1>Pending aura suggestions</h1>
      {pending.length === 0 && <p>Nothing to review.</p>}
      {pending.map((item: any) => (
        <div key={item.id} style={{ border: "1px solid #333", padding: 12, marginBottom: 8 }}>
          <p>User: {item.user_id}</p>
          <p>Suggested points: {item.points}</p>
          <p>Note: {item.note}</p>
          <ReviewButtons auraId={item.id} />
        </div>
      ))}
    </main>
  );
}
