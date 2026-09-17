"use client";

import { reviewAura } from "@/lib/api";

const ADMIN_ID = process.env.NEXT_PUBLIC_ADMIN_ID ?? "";

export default function ReviewButtons({ auraId }: { auraId: string }) {
  return (
    <div>
      <button onClick={() => reviewAura(auraId, ADMIN_ID, "approved")}>Approve</button>
      <button onClick={() => reviewAura(auraId, ADMIN_ID, "rejected")}>Reject</button>
    </div>
  );
}
