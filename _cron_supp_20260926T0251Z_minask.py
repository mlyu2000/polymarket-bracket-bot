"""Supplement: correct best-ask (min) near-miss floor, liq>0 guard, same as prior runs."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        if yp <= 0 or np_ <= 0 or yp >= 1 or np_ >= 1:
            continue
        priced += 1
        rows.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    rows.sort()
    return priced, dt, rows

priced, dt, rows = asyncio.run(scan())
print(f"[supplement min-ask] {priced} priced markets in {dt:.1f}s")
print("FLOOR (true best-ask sums, lowest 10):")
for s, q, yp, np_, liq in rows[:10]:
    flag = " <<BRACKET" if s < 1.0 else ""
    print(f"  {s:.4f} | Y@{yp:.3f} N@{np_:.3f} | liq={liq:.0f} | {q}{flag}")
print(f"count sum<1.00: {sum(1 for r in rows if r[0] < 1.0)}")
print(f"count sum<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
