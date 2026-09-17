"use client";

import { getLeaderboard } from "@/lib/api";
import { useEffect, useState } from "react";

const Sidebar = ({ leaderboard, onToggleSidebar, width }: { leaderboard: any[]; onToggleSidebar: () => void; width: number }) => {
  return (
    <aside style={{
      width,
      padding: 20,
      background: "#080a0f",
      color: "#eee",
      height: "100vh",
      position: "fixed",
      left: 0,
      top: 0,
      overflowY: "auto",
      boxSizing: "border-box",
      transition: "width 0.3s ease",
      zIndex: 1000,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h2 style={{ color: "#7dd3fc", margin: 0 }}>Leaderboard</h2>
        <button onClick={onToggleSidebar} style={{
          background: "transparent",
          border: "none",
          color: "#eee",
          fontSize: 20,
          cursor: "pointer",
          padding: 0,
          lineHeight: 1,
        }}>
          ×
        </button>
      </div>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th style={{ textAlign: "left", padding: 4 }}>Friend</th>
            <th style={{ textAlign: "right", padding: 4 }}>Price</th>
          </tr>
        </thead>
        <tbody>
          {leaderboard.map((row: any) => (
            <tr key={row.user_id} style={{ borderBottom: "1px solid #1f2937" }}>
              <td style={{ textAlign: "left", padding: 4 }}>
                <a href={`/friend/${row.user_id}`} style={{ color: "#7dd3fc", textDecoration: "none" }}>
                  {row.user_id}
                </a>
              </td>
              <td style={{ textAlign: "right", padding: 4 }}>${row.price.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </aside>
  );
};

const Graph = ({ leaderboard }: { leaderboard: any[] }) => {
  const [data, setData] = useState<Record<string, any[]>>({});
  const [loading, setLoading] = useState(true);
  const [tooltip, setTooltip] = useState<{
    x: number;
    y: number;
    userId: string;
    timestamp: number;
    price: number
  } | null>(null);
  const [hoveredLegendItem, setHoveredLegendItem] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    // Simulate loading delay
    const timer = setTimeout(() => {
      // Generate dummy data for each user
      const dummyData: Record<string, any[]> = {};
      leaderboard.forEach((row: any) => {
        const userId = row.user_id;
        // Generate 30 days of data
        const history = [];
        const basePrice = 10 + Math.random() * 90; // random between 10 and 100
        let price = basePrice;
        for (let i = 29; i >= 0; i--) {
          const date = new Date();
          date.setDate(date.getDate() - i);
          // Random walk: change by -2 to +2
          price += (Math.random() - 0.5) * 4;
          // Ensure price stays positive
          if (price < 1) price = 1;
          history.push({
            timestamp: date.getTime(),
            price: Number(price.toFixed(2)),
          });
        }
        dummyData[userId] = history;
      });
      setData(dummyData);
      setLoading(false);
    }, 500);

    return () => {
      clearTimeout(timer);
    };
  }, [leaderboard]);

  if (loading) {
    return <div style={{ padding: 40, textAlign: "center" }}>Loading chart...</div>;
  }

  // Flatten all points to get domains
  const allPoints: { timestamp: number; price: number }[] = [];
  Object.values(data).forEach((history) => {
    allPoints.push(...history);
  });

  if (allPoints.length === 0) {
    return <div style={{ padding: 40, textAlign: "center" }}>No data available</div>;
  }

  const minTime = Math.min(...allPoints.map((p) => p.timestamp));
  const maxTime = Math.max(...allPoints.map((p) => p.timestamp));
  const minPrice = Math.min(...allPoints.map((p) => p.price));
  const maxPrice = Math.max(...allPoints.map((p) => p.price));

  // Add some padding
  const timeRange = maxTime - minTime;
  const priceRange = maxPrice - minPrice;
  const paddedMinTime = minTime - timeRange * 0.05;
  const paddedMaxTime = maxTime + timeRange * 0.05;
  const paddedMinPrice = minPrice - priceRange * 0.1;
  const paddedMaxPrice = maxPrice + priceRange * 0.1;

  // Guard against zero range
  const safeTimeRange = paddedMaxTime - paddedMinTime || 1;
  const safePriceRange = paddedMaxPrice - paddedMinPrice || 1;

  // We'll let the SVG scale to its container via width="100%" height="100%" and viewBox
  const viewBoxWidth = 1000; // arbitrary, will scale
  const viewBoxHeight = 500;
  const padding = { top: 20, right: 30, bottom: 40, left: 60 };
  const chartWidth = viewBoxWidth - padding.left - padding.right;
  const chartHeight = viewBoxHeight - padding.top - padding.bottom;

  const xScale = (timestamp: number) =>
    padding.left + ((timestamp - paddedMinTime) / safeTimeRange) * chartWidth;
  const yScale = (price: number) =>
    viewBoxHeight -
    padding.bottom -
    ((price - paddedMinPrice) / safePriceRange) * chartHeight;

  // Generate a color palette (simple)
  const colors = ["#7dd3fc", "#fbbf24", "#86efac", "#f87171", "#a78bfa", "#ec4899", "#10b981"];
  const getColor = (index: number) => colors[index % colors.length];

  // Handle mouse move on SVG for tooltip
  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const svg = e.currentTarget;
    const rect = svg.getBoundingClientRect();
    const svgX = e.clientX - rect.left;
    const svgY = e.clientY - rect.top;

    // Find closest data point
    let closestPoint = null;
    let minDistance = Infinity;

    Object.entries(data).forEach(([userId, history]) => {
      history.forEach(point => {
        const pointX = xScale(point.timestamp);
        const pointY = yScale(point.price);
        const distance = Math.sqrt(
          Math.pow(svgX - pointX, 2) +
          Math.pow(svgY - pointY, 2)
        );
        if (distance < minDistance && distance < 15) { // 15px tolerance
          minDistance = distance;
          closestPoint = {
            x: pointX,
            y: pointY,
            userId,
            timestamp: point.timestamp,
            price: point.price
          };
        }
      });
    });

    setTooltip(closestPoint);
  };

  const handleMouseLeave = () => {
    setTooltip(null);
  };

  return (
    <div style={{ position: "relative", width: "100%", height: "100%" }}>
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
        preserveAspectRatio="xMidYMid meet"
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        style={{ cursor: "crosshair" }}
      >
        {/* Background */}
        <rect
          width={viewBoxWidth}
          height={viewBoxHeight}
          fill="#0b0d12"
        />

        {/* Grid lines */}
        {/* Horizontal grid lines */}
        {[0, 0.2, 0.4, 0.6, 0.8, 1].map((ratio) => {
          const y = viewBoxHeight - padding.bottom - ratio * chartHeight;
          return (
            <line
              key={`h-grid-${ratio}`}
              x1={padding.left}
              y1={y}
              x2={viewBoxWidth - padding.right}
              y2={y}
              stroke="#1f2937"
              strokeWidth={1}
              strokeDasharray="2,2"
            />
          );
        })}
        {/* Vertical grid lines */}
        {[0, 0.2, 0.4, 0.6, 0.8, 1].map((ratio) => {
          const x = padding.left + ratio * chartWidth;
          return (
            <line
              key={`v-grid-${ratio}`}
              x1={x}
              y1={padding.top}
              x2={x}
              y2={viewBoxHeight - padding.bottom}
              stroke="#1f2937"
              strokeWidth={1}
              strokeDasharray="2,2"
            />
          );
        })}

        {/* Title */}
        <text
          x={viewBoxWidth / 2}
          y={padding.top / 2}
          textAnchor="middle"
          fill="#eee"
          fontSize={16}
          fontWeight="600"
        >
          Stock Price History
        </text>

        {/* Axes */}
        <line
          x1={padding.left}
          y1={viewBoxHeight - padding.bottom}
          x2={viewBoxWidth - padding.right}
          y2={viewBoxHeight - padding.bottom}
          stroke="#374151"
          strokeWidth={1}
        />
        <line
          x1={padding.left}
          y1={padding.top}
          x2={padding.left}
          y2={viewBoxHeight - padding.bottom}
          stroke="#374151"
          strokeWidth={1}
        />

        {/* X axis ticks and labels */}
        {[0, 0.2, 0.4, 0.6, 0.8, 1].map((ratio) => {
          const x = padding.left + ratio * chartWidth;
          const date = new Date(paddedMinTime + ratio * safeTimeRange);
          const label = date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
          return (
            <g key={ratio}>
              <line
                x1={x}
                y1={viewBoxHeight - padding.bottom}
                x2={x}
                y2={viewBoxHeight - padding.bottom + 4}
                stroke="#374151"
                strokeWidth={1}
              />
              <text
                x={x}
                y={viewBoxHeight - padding.bottom + 20}
                textAnchor="middle"
                fill="#9ca3af"
                fontSize={12}
              >
                {label}
              </text>
            </g>
          );
        })}

        {/* Y axis ticks and labels */}
        {[0, 0.2, 0.4, 0.6, 0.8, 1].map((ratio) => {
          const y = viewBoxHeight - padding.bottom - ratio * chartHeight;
          const price = paddedMinPrice + ratio * safePriceRange;
          return (
            <g key={ratio}>
              <line
                x1={padding.left - 4}
                y1={y}
                x2={padding.left}
                y2={y}
                stroke="#374151"
                strokeWidth={1}
              />
              <text
                x={padding.left - 8}
                y={y + 4}
                textAnchor="end"
                fill="#9ca3af"
                fontSize={12}
              >
                ${price.toFixed(2)}
              </text>
            </g>
          );
        })}

        {/* Axis labels */}
        <text
          x={viewBoxWidth / 2}
          y={viewBoxHeight - padding.bottom / 2}
          textAnchor="middle"
          fill="#9ca3af"
          fontSize={12}
        >
          Date
        </text>
        <text
          x={-viewBoxHeight / 2}
          y={padding.left / 2}
          textAnchor="middle"
          transform={`rotate(-90)`}
          fill="#9ca3af"
          fontSize={12}
        >
          Price ($)
        </text>

        {/* Lines with animated drawing effect */}
        {Object.entries(data).map(([userId, history], idx) => {
          if (history.length === 0) return null;
          const points = history
            .map((p) => `${xScale(p.timestamp)},${yScale(p.price)}`)
            .join(" ");
          return (
            <polyline
              key={userId}
              points={points}
              fill="none"
              stroke={getColor(idx)}
              strokeWidth={2}
              strokeLinejoin="round"
              strokeLinecap="round"
            />
          );
        })}

        {/* Current price points (dots at end of each line) */}
        {Object.entries(data).map(([userId, history], idx) => {
          if (history.length === 0) return null;
          const latest = history[history.length - 1]; // Most recent point
          return (
            <circle
              key={`${userId}-point`}
              cx={xScale(latest.timestamp)}
              cy={yScale(latest.price)}
              r={4}
              fill={getColor(idx)}
            />
          );
        })}

        {/* Tooltip */}
        {tooltip && (
          <g>
            {/* Tooltip background */}
            <rect
              x={tooltip.x + 10}
              y={tooltip.y - 20}
              width={80}
              height={30}
              rx={4}
              ry={4}
              fill="#1f2937"
              stroke="#374151"
              strokeWidth={1}
            />
            {/* Tooltip text */}
            <text
              x={tooltip.x + 14}
              y={tooltip.y - 5}
              fill="#eee"
              fontSize={12}
            >
              {tooltip.userId}: ${tooltip.price.toFixed(2)}
            </text>
            <text
              x={tooltip.x + 14}
              y={tooltip.y + 12}
              fill="#9ca3af"
              fontSize={10}
            >
              {new Date(tooltip.timestamp).toLocaleDateString()}
            </text>
            {/* Tooltip pointer */}
            <polygon
              points={`${tooltip.x},${tooltip.y} ${tooltip.x + 5},${tooltip.y - 8} ${tooltip.x + 5},${tooltip.y + 8}`
              fill="#1f2937"
            />
          </g>
        )}
      </svg>

      {/* Legend */}
      <div style={{
        position: "absolute",
        top: 10,
        right: 10,
        display: "flex",
        gap: "12px",
        fontSize: 14,
        pointerEvents: "all",
      }}>
        {Object.entries(data).map(([userId, history], idx) => (
          <div
            key={userId}
            onMouseEnter={() => setHoveredLegendItem(userId)}
            onMouseLeave={() => setHoveredLegendItem(null)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 4,
              cursor: "pointer",
              padding: "2px 4px",
              borderRadius: "4px",
              backgroundColor: hoveredLegendItem === userId ? "#374151" : "transparent",
              transition: "background-color 0.2s ease",
            }}
            onClick={() => {
              // Toggle visibility - for now just console log
              console.log(`Toggled visibility for ${userId}`);
            }}
          >
            <div
              style={{
                width: 12,
                height: 12,
                background: getColor(idx),
                borderRadius: 2,
              }}
            />
            <span style={{ color: "#eee" }}>{userId}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default function HomePage() {
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usingDummy, setUsingDummy] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Generate dummy leaderboard data for fallback
  const generateDummyLeaderboard = () => {
    const dummyUsers = [
      { id: "alice", price: 42.50 },
      { id: "bob", price: 38.75 },
      { id: "charlie", price: 55.20 },
      { id: "diana", price: 29.90 },
      { id: "eve", price: 67.30 },
    ];
    return dummyUsers.map(({ id, price }) => ({
      user_id: id,
      price: price,
      fundamentals_score: Math.random() * 100, // dummy
    }));
  };

  useEffect(() => {
    const fetchLeaderboard = async () => {
      setLoading(true);
      setError(null);
      try {
        const rows = await getLeaderboard();
        if (rows && rows.length > 0) {
          setLeaderboard(rows);
          setUsingDummy(false);
        } else {
          // empty array, fallback to dummy
          const dummy = generateDummyLeaderboard();
          setLeaderboard(dummy);
          setUsingDummy(true);
          setError("Using dummy leaderboard data (backend empty)");
        }
      } catch (err) {
        console.error("Failed to fetch leaderboard", err);
        const dummy = generateDummyLeaderboard();
        setLeaderboard(dummy);
        setUsingDummy(true);
        setError("Failed to load leaderboard, using dummy data");
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, []);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", background: "#0b0d12", color: "#eee", position: "relative" }}>
        <div style={{ padding: 40, textAlign: "center" }}>Loading...</div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0b0d12", color: "#eee", position: "relative" }}>
      {/* Sidebar toggle button (shown when sidebar is closed) */}
      {!sidebarOpen && (
        <button
          onClick={toggleSidebar}
          style={{
            position: "fixed",
            left: 20,
            top: 20,
            background: "#374151",
            border: "none",
            color: "#eee",
            width: 36,
            height: 36,
            borderRadius: "4px",
            fontSize: 20,
            cursor: "pointer",
            zIndex: 1100,
          }}
        >
          ☰
        </button>
      )}

      {/* Sidebar (collapsible) */}
      <Sidebar
        leaderboard={leaderboard}
        onToggleSidebar={toggleSidebar}
        width={sidebarOpen ? 260 : 0}
        style={{ overflow: sidebarOpen ? "visible" : "hidden" }}
      />

      {/* Main content */}
      <div
        style={{
          marginLeft: sidebarOpen ? 260 : 0,
          transition: "margin-left 0.3s ease",
          minHeight: "100vh",
          padding: 20,
          boxSizing: "border-box",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {usingDummy && (
          <div style={{
            background: "#1f2937",
            border: "1px solid #374151",
            color: "#fbbf24",
            padding: "8px 16px",
            marginBottom: "16px",
            borderRadius: "4px",
            fontSize: "14px",
            alignSelf: "flex-start",
          }}>
            ⚠️ Using dummy data - backend not available or empty
          </div>
        )}
        {!usingDummy && error && (
          <div style={{ padding: 10, textAlign: "center", color: "#f87171", marginBottom: "16px" }}>
            {error}
          </div>
        )}
        <h1 style={{ color: "#7dd3fc", margin: 0, marginBottom: 24, flexShrink: 0 }}>Welcome to PeerIPO</h1>
        <div style={{ flexGrow: 1 }}>
          <Graph leaderboard={leaderboard} />
        </div>
      </div>
    </div>
  );
}