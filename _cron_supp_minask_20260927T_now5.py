import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    sums = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            priced += 1
            sums.append((ya + na, m.question[:55], ya, na, m.liquidity))
    sums.sort()
    return len(markets), priced, sums

markets, priced, sums = asyncio.run(supp())
print(f"Markets fetched: {markets}, priced books: {priced}")
print("Top 10 lowest min-ask sums (true floor):")
for s, q, ya, na, liq in sums[:10]:
    flag = " *** BRACKET ***" if s < 1.0 else ""
    print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}{flag}")
print(f"Count sum<=1.005: {sum(1 for x in sums if x[0] <= 1.005)}")
print(f"Count sum<=1.01: {sum(1 for x in sums if x[0] <= 1.01)}")
