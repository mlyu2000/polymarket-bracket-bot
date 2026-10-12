# Supplementary: min-ask floor check (asks[0] in the verbatim script is DESC-sorted
# worst ask ~0.999 per CLOB /book ordering, so its near-miss bucket is always empty).
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            y = min(float(a['price']) for a in yb.asks)
            n = min(float(a['price']) for a in nb.asks)
            rows.append((y + n, m.question[:60], y, n, m.liquidity))
    rows.sort()
    return priced, rows

priced, rows = asyncio.run(scan())
print(f"[supp] priced markets: {priced}")
brackets = [r for r in rows if r[0] < 1.0]
print(f"[supp] min-ask brackets (<1.000): {len(brackets)}")
for s, q, y, n, l in brackets[:10]:
    print(f"  {s:.4f} | Y@{y:.3f} N@{n:.3f} | liq={l} | {q}")
print("[supp] top-5 min-ask floors:")
for s, q, y, n, l in rows[:5]:
    print(f"  {s:.4f} | Y@{y:.3f} N@{n:.3f} | liq={l} | {q}")
