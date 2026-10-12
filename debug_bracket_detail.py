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
        if y and n and y.asks and n.asks:
            yes_min = min(y.asks, key=lambda a: float(a["price"]))
            no_min = min(n.asks, key=lambda a: float(a["price"]))
            total = float(yes_min["price"])+float(no_min["price"])
            if total < 1.01:
                print(m.question[:80])
                print("total", total)
                print("yes price min", yes_min)
                print("no price min", no_min)
                print("yes asks len", len(y.asks))
                print("no asks len", len(n.asks))
                print("---")
                break

asyncio.run(test())
