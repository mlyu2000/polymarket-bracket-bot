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
    near = []
    brackets = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            total = yp + np_
            priced += 1
            if total < 1.0:
                brackets.append((total, m.question[:60], yp, np_, m.liquidity))
            elif total <= 1.005:
                near.append((total, m.question[:60], yp, np_, m.liquidity))
    near.sort()
    brackets.sort()
    return priced, brackets, near

priced, brackets, near = asyncio.run(scan())
print(f"priced markets: {priced}")
print(f"TRUE brackets (min-ask sum < 1.00): {len(brackets)}")
for total, q, yp, np_, liq in brackets[:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"min-ask near-misses (<=1.005): {len(near)}")
for total, q, yp, np_, liq in near[:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
