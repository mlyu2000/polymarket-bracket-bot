import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np_, m.question, yp, np_, m.liquidity))

    brackets = sorted([r for r in rows if r[0] < 1.0])
    near = sorted([r for r in rows if 1.0 <= r[0] <= 1.005])
    return len(markets), len(rows), brackets, near

nmark, npriced, brackets, near = asyncio.run(scan())
print(f"📐 CORRECTED (best-ask = min over asks): {npriced}/{nmark} books priced")
print(f"✅ TRUE BRACKETS (best sum < 1.00): {len(brackets)}")
for t, q, yp, np_, liq in brackets[:10]:
    print(f"  🔴 sum={t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q[:70]}")
print(f"📊 Near-misses (1.000–1.005): {len(near)}")
for t, q, yp, np_, liq in near[:8]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q[:70]}")
