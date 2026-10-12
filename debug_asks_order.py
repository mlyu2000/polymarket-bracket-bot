import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def run():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    target = "Will the highest temperature in Busan be 28°C on August 23?"
    for m in markets:
        if target in m.question:
            print(m.question)
            print(m.clob_token_ids)
            yes_id, no_id = m.clob_token_ids
            yes_book = await api.fetch_order_book(yes_id)
            no_book = await api.fetch_order_book(no_id)
            print("yes asks first 5:", yes_book.asks[:5])
            print("no asks first 5:", no_book.asks[:5])
            # compute min
            y_min = min(yes_book.asks, key=lambda a: float(a["price"]))
            n_min = min(no_book.asks, key=lambda a: float(a["price"]))
            print("min yes", y_min)
            print("min no", n_min)
            print("sum min", float(y_min["price"])+float(n_min["price"]))
            # asks[0]
            print("asks0 sum", float(yes_book.asks[0]["price"])+float(no_book.asks[0]["price"]))
            break

asyncio.run(run())
