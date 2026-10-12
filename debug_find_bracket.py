import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    for m,(y,n) in zip(markets, all_books):
        if not y or not n: continue
        if not y.asks or not n.asks: continue
        yes_min = min(y.asks, key=lambda a: float(a["price"]))
        no_min = min(n.asks, key=lambda a: float(a["price"]))
        yp = float(yes_min["price"])
        np = float(no_min["price"])
        total = yp+np
        if total < 1.0:
            print("FOUND", total, m.question[:80])
            print("liquidity", m.liquidity)
            print("yes price", yp, "size", yes_min["size"])
            print("no price", np, "size", no_min["size"])
            break

asyncio.run(test())
