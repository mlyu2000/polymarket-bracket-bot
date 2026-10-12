import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=20)
    for m in markets:
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = float(yes_book.asks[0]['price'])
            np = float(no_book.asks[0]['price'])
            s = yp+np
            if s < 1.1:
                print(f"LOW SUM {s:.3f} {m.question[:60]} yes {yp} no {np}")
        await asyncio.sleep(0.05)

asyncio.run(check())
