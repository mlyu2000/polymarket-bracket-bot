import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        if yp <= 0 or np <= 0 or yp >= 1 or np >= 1:
            continue
        priced += 1
        rows.append((yp + np, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    return priced, rows

priced, rows = asyncio.run(scan())
print(f"best-ask priced markets: {priced}")
brackets = [r for r in rows if r[0] < 1.0]
print(f"true brackets (best-ask sum < 1.00): {len(brackets)}")
for s, q, yp, np, liq in brackets[:10]:
    print(f"  {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print("top-10 best sums:")
for s, q, yp, np, liq in rows[:10]:
    print(f"  {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
