"use client";

import { FormEvent, useEffect, useState } from "react";

import { AnalyticsTabs } from "@/components/analytics/AnalyticsTabs";
import { AppShell } from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { apiClient } from "@/lib/api-client";
import type { PortfolioSummary, Trade, TradeSide } from "@/lib/types";

function currency(n: number) {
  const sign = n < 0 ? "-" : "";
  return `${sign}$${Math.abs(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function PortfolioPage() {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);

  const [symbol, setSymbol] = useState("");
  const [side, setSide] = useState<TradeSide>("buy");
  const [quantity, setQuantity] = useState("");
  const [price, setPrice] = useState("");
  const [tradeDate, setTradeDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [submitting, setSubmitting] = useState(false);

  function refresh() {
    setLoading(true);
    return Promise.all([
      apiClient.get<PortfolioSummary>("/trades/portfolio").then(setSummary),
      apiClient.get<Trade[]>("/trades").then(setTrades),
    ]).finally(() => setLoading(false));
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!symbol.trim() || !quantity || !price) return;
    setSubmitting(true);
    try {
      await apiClient.post("/trades", {
        symbol: symbol.trim().toUpperCase(),
        side,
        quantity: Number(quantity),
        price: Number(price),
        trade_date: tradeDate,
      });
      setSymbol("");
      setQuantity("");
      setPrice("");
      await refresh();
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(tradeId: string) {
    await apiClient.delete(`/trades/${tradeId}`);
    await refresh();
  }

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-medium mb-1">Analytics</h1>
      <p className="text-night-text-muted mb-2">
        Log trades manually for now — live pricing is on the roadmap.
      </p>
      <AnalyticsTabs />

      <Card className="mb-5">
        <CardHeader title="Log a trade" />
        <form onSubmit={handleSubmit} className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <Input
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            placeholder="Symbol (e.g. AAPL)"
            className="col-span-2 md:col-span-1"
          />
          <select
            value={side}
            onChange={(e) => setSide(e.target.value as TradeSide)}
            className="input-field"
          >
            <option value="buy">Buy</option>
            <option value="sell">Sell</option>
          </select>
          <Input
            type="number"
            step="any"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            placeholder="Quantity"
          />
          <Input
            type="number"
            step="any"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            placeholder="Price"
          />
          <Input
            type="date"
            value={tradeDate}
            onChange={(e) => setTradeDate(e.target.value)}
          />
          <Button type="submit" disabled={submitting} className="col-span-2 md:col-span-5">
            {submitting ? "Logging…" : "Log trade"}
          </Button>
        </form>
      </Card>

      {loading ? (
        <p className="text-sm text-night-text-muted">Loading…</p>
      ) : (
        <div className="space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <Card>
              <CardHeader title="Realized P&L" />
              <p
                className={`text-3xl font-display ${
                  (summary?.total_realized_pl ?? 0) >= 0 ? "text-positive" : "text-danger"
                }`}
              >
                {currency(summary?.total_realized_pl ?? 0)}
              </p>
            </Card>
            <Card>
              <CardHeader title="Cost basis (open positions)" />
              <p className="text-3xl font-display text-night-text">{currency(summary?.total_cost_basis ?? 0)}</p>
            </Card>
          </div>

          <Card>
            <CardHeader title="Positions" />
            {!summary || summary.positions.length === 0 ? (
              <p className="text-sm text-night-text-muted">No open positions yet.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-night-text-muted text-xs uppercase tracking-wide">
                      <th className="pb-2 font-medium">Symbol</th>
                      <th className="pb-2 font-medium">Quantity</th>
                      <th className="pb-2 font-medium">Avg cost</th>
                      <th className="pb-2 font-medium">Total cost</th>
                      <th className="pb-2 font-medium">Realized P&L</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-night-border">
                    {summary.positions.map((p) => (
                      <tr key={p.symbol}>
                        <td className="py-2.5 font-medium text-night-text">{p.symbol}</td>
                        <td className="py-2.5 text-night-text-muted">{p.quantity}</td>
                        <td className="py-2.5 text-night-text-muted">{currency(p.average_cost)}</td>
                        <td className="py-2.5 text-night-text-muted">{currency(p.total_cost)}</td>
                        <td className={`py-2.5 ${p.realized_pl >= 0 ? "text-positive" : "text-danger"}`}>
                          {currency(p.realized_pl)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>

          <Card>
            <CardHeader title="Trade history" />
            {trades.length === 0 ? (
              <p className="text-sm text-night-text-muted">No trades logged yet.</p>
            ) : (
              <ul className="divide-y divide-night-border">
                {trades.map((t) => (
                  <li key={t.id} className="flex items-center justify-between py-3 text-sm">
                    <div className="flex items-center gap-3">
                      <Badge variant={t.side === "buy" ? "positive" : "high"}>{t.side}</Badge>
                      <span className="text-night-text font-medium">{t.symbol}</span>
                      <span className="text-night-text-muted">
                        {t.quantity} @ {currency(t.price)}
                      </span>
                      <span className="text-night-text-muted">{new Date(t.trade_date).toLocaleDateString()}</span>
                    </div>
                    <button
                      onClick={() => handleDelete(t.id)}
                      className="text-xs text-night-text-muted hover:text-danger transition"
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>
      )}
    </AppShell>
  );
}