import asyncio
from polymarket_api import PolymarketAPI
from config import Config

async def f():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=50)
    for m in markets:
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = float(yes_book.asks[0]['price'])
            np = float(no_book.asks[0]['price'])
            if 0.4 < yp < 0.6 and 0.4 < np < 0.6:
                print(m.question[:80])
                print(f"yes ask {yp} no ask {np} sum {yp+np}")
                print("yes asks:", [a['price'] for a in yes_book.asks[:5]])
                print("no asks:", [a['price'] for a in no_book.asks[:5]])
                break
        await asyncio.sleep(0.05)

asyncio.run(f())
