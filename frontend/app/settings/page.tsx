"use client";

import { useState } from "react";
import { setOptIn } from "@/lib/api";

const CATEGORIES = ["location", "canvas", "spotify", "aura", "stock_visible"];

export default function SettingsPage() {
  const [userId, setUserId] = useState("");
  const [status, setStatus] = useState<string | null>(null);

  async function toggle(category: string, enabled: boolean) {
    if (!userId) return;
    await setOptIn(userId, category, enabled);
    setStatus(`${category} set to ${enabled}`);
  }

  return (
    <main style={{ padding: 24 }}>
      <h1>Your opt-ins</h1>
      <input
        placeholder="your user id"
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
        style={{ marginBottom: 16, display: "block" }}
      />
      {CATEGORIES.map((category) => (
        <div key={category} style={{ marginBottom: 8 }}>
          <span style={{ marginRight: 12 }}>{category}</span>
          <button onClick={() => toggle(category, true)}>Enable</button>
          <button onClick={() => toggle(category, false)}>Disable</button>
        </div>
      ))}
      {status && <p>{status}</p>}
    </main>
  );
}
