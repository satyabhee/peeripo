import { getStockHistory } from "@/lib/api";

export default async function FriendPage({ params }: { params: { id: string } }) {
  const history = await getStockHistory(params.id);

  return (
    <main style={{ padding: 24 }}>
      <h1>Stock history</h1>
      <ul>
        {history.map((point: any) => (
          <li key={point.recorded_at}>
            {new Date(point.recorded_at).toLocaleDateString()}: ${point.price.toFixed(2)}
          </li>
        ))}
      </ul>
    </main>
  );
}
