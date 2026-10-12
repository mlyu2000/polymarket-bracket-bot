import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    brackets = []
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        tot = yp + np_
        if tot < 1.0:
            brackets.append((tot, m.question[:70], yp, np_, m.liquidity))
        elif tot <= 1.005:
            rows.append((tot, m.question[:70], yp, np_, m.liquidity))
    rows.sort()
    brackets.sort()
    return len(markets), brackets, rows

n, brackets, near = asyncio.run(scan())
print(f"Markets scanned: {n}")
print(f"BEST-ASK BRACKETS (sum<1.00): {len(brackets)}")
for t, q, yp, np_, liq in brackets:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"BEST-ASK NEAR-MISSES (<=1.005): {len(near)}")
for t, q, yp, np_, liq in near[:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if not near and not brackets:
    # report overall floor for context
    pass
