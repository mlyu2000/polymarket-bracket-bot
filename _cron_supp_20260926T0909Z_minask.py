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

    near = []
    brackets_minask = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        total = yp + np_
        if total < 1.0 and m.liquidity > 0:
            brackets_minask.append((total, m.question[:60], yp, np_, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:50], yp, np_, m.liquidity))
    near.sort()
    brackets_minask.sort()
    return brackets_minask, near

b, n = asyncio.run(scan())
print(f"[min-ask] True sum<1.00 (any liq): {len(b)}")
for t, q, yp, np_, liq in b[:10]:
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"[min-ask] Near-misses (1.00<sum<=1.005): {len(n)}")
for t, q, yp, np_, liq in n[:10]:
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
