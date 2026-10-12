import asyncio, logging, time
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
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            rows.append((ya+na, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
brackets = [r for r in rows if r[0] < 1.0]
print(f"Markets with priced books: {len(rows)}")
print(f"TRUE brackets (best-ask sum < 1.00): {len(brackets)}")
for s,q,ya,na,liq in brackets[:10]:
    print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
print("10 lowest sums (min-ask):")
for s,q,ya,na,liq in rows[:10]:
    print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
