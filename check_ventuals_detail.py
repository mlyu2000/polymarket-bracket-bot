import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    for m in markets:
        if "Ventuals FDV above" in m.question:
            print("FOUND:", m.question)
            yes_id, no_id = m.clob_token_ids
            yes_book = await api.fetch_order_book(yes_id)
            no_book = await api.fetch_order_book(no_id)
            if yes_book and yes_book.asks:
                print("Yes asks first 5:", yes_book.asks[:5])
                print("Yes min:", min(yes_book.asks, key=lambda a: float(a['price'])))
            if no_book and no_book.asks:
                print("No asks first 5:", no_book.asks[:5])
                print("No min:", min(no_book.asks, key=lambda a: float(a['price'])))
            # compute using asks[0]
            yes_price0 = float(yes_book.asks[0]['price'])
            no_price0 = float(no_book.asks[0]['price'])
            print(f"asks[0] sum: {yes_price0 + no_price0}")
            # compute using min
            yes_price_min = float(min(yes_book.asks, key=lambda a: float(a['price']))['price'])
            no_price_min = float(min(no_book.asks, key=lambda a: float(a['price']))['price'])
            print(f"min sum: {yes_price_min + no_price_min}")
            break

asyncio.run(test())
