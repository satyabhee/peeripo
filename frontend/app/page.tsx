import { getLeaderboard } from "@/lib/api";

export default async function LeaderboardPage() {
  const rows = await getLeaderboard();

  return (
    <main style={{ padding: 24 }}>
      <h1>PeerIPO Leaderboard</h1>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th style={{ textAlign: "left" }}>Friend</th>
            <th style={{ textAlign: "right" }}>Price</th>
            <th style={{ textAlign: "right" }}>Fundamentals</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row: any) => (
            <tr key={row.user_id}>
              <td>
                <a href={`/friend/${row.user_id}`} style={{ color: "#7dd3fc" }}>
                  {row.user_id}
                </a>
              </td>
              <td style={{ textAlign: "right" }}>${row.price.toFixed(2)}</td>
              <td style={{ textAlign: "right" }}>{row.fundamentals_score.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
