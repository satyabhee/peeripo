const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function getLeaderboard() {
  const res = await fetch(`${API_BASE}/stocks/leaderboard`, { cache: "no-store" });
  return res.json();
}

export async function getStockHistory(userId: string) {
  const res = await fetch(`${API_BASE}/stocks/${userId}/history`, { cache: "no-store" });
  return res.json();
}

export async function getPendingAura() {
  const res = await fetch(`${API_BASE}/aura/pending`, { cache: "no-store" });
  return res.json();
}

export async function reviewAura(auraId: string, adminId: string, status: string, points?: number) {
  const res = await fetch(`${API_BASE}/aura/${auraId}/review?admin_id=${adminId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status, points }),
  });
  return res.json();
}

export async function setOptIn(userId: string, category: string, enabled: boolean) {
  const res = await fetch(`${API_BASE}/users/${userId}/opt-ins`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ category, enabled }),
  });
  return res.json();
}
