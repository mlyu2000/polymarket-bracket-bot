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
            total_min = float(yes_min["price"])+float(no_min["price"])
            if total_min <= 1.005:
                print("MARKET", m.question[:80])
                print("liquidity", m.liquidity)
                print("yes asks first 3", y.asks[:3])
                print("no asks first 3", n.asks[:3])
                print("min yes", yes_min)
                print("min no", no_min)
                print("total", total_min)
                break

asyncio.run(test())
