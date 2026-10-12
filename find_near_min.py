import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    near = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yes_min = min(yb.asks, key=lambda a: float(a['price']))
        no_min = min(nb.asks, key=lambda a: float(a['price']))
        total = float(yes_min['price']) + float(no_min['price'])
        if total <= 1.005:
            near.append((total, m.question[:60], float(yes_min['price']), float(no_min['price'])))
    near.sort()
    print(f"Near misses with min: {len(near)}")
    for total, q, yp, np in near[:20]:
        print(f"{total:.4f} | Yes {yp:.4f} No {np:.4f} | {q}")

asyncio.run(test())
