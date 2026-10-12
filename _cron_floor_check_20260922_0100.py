import asyncio, json, logging, time
from datetime import datetime, timezone
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks and m.liquidity > 0:
            y = min(float(a['price']) for a in yb.asks)
            n = min(float(a['price']) for a in nb.asks)
            rows.append((round(y + n, 4), m.question[:60], y, n, m.liquidity))
    rows.sort()
    return rows, time.time() - t0, len(markets)

rows, elapsed, nm = asyncio.run(scan())
brackets = [r for r in rows if r[0] < 1.0]
near = [r for r in rows if r[0] <= 1.005]
print(f"min-ask scan: {nm} markets in {elapsed:.1f}s | priced={len(rows)}")
print(f"true brackets (<1.0): {len(brackets)}")
for t, q, y, n, liq in brackets[:10]:
    print(f"  {t:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq:.0f} | {q}")
print(f"near <=1.005: {len(near)}")
for t, q, y, n, liq in near[:8]:
    print(f"  {t:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq:.0f} | {q}")

out = {
    'ts': datetime.now(timezone.utc).isoformat(),
    'markets': nm, 'priced': len(rows),
    'scan_seconds': round(elapsed, 1),
    'method': 'min-ask',
    'brackets': [list(b) for b in brackets],
    'near_le_1005': [list(x) for x in near],
    'floor': rows[0][0] if rows else None,
}
fn = f"runs/cron_scan_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}Z.json"
with open(fn, 'w') as f:
    json.dump(out, f, indent=1)
print(f"saved {fn}")
