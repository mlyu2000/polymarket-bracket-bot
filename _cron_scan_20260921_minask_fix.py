import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0
    rows = []
    brackets = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            tot = yp + np_
            if tot < 1.0:
                brackets.append((tot, m.question[:60], yp, np_, m.liquidity))
            if tot <= 1.005:
                rows.append((tot, m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    brackets.sort()
    return len(markets), dt, brackets, rows

n, dt, brackets, rows = asyncio.run(scan())
print(f"Markets: {n} in {dt:.1f}s (min-ask corrected)")
print(f"BRACKETS (min-ask sum < 1.00): {len(brackets)}")
for t, q, yp, np_, liq in brackets[:10]:
    print(f"  {t:.3f} | Y@{yp:.3f} N@{np_:.3f} | liq={liq} | {q}")
print(f"Near-misses (min-ask sum <= 1.005): {len(rows)}")
for t, q, yp, np_, liq in rows[:10]:
    print(f"  {t:.3f} | Y@{yp:.3f} N@{np_:.3f} | liq={liq} | {q}")
