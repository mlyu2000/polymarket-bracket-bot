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
    near = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            total = yp + np_
            priced += 1
            if total <= 1.005:
                near.append((total, m.question[:60], yp, np_, m.liquidity))
    near.sort()
    return priced, near

priced, near = asyncio.run(scan())
print(f"priced markets: {priced}")
print(f"min-ask near-misses (<=1.005): {len(near)}")
for total, q, yp, np_, liq in near[:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
