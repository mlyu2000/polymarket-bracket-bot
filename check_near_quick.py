import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=200)
    print(f"Markets: {len(markets)}")
    counts = 0
    for m in markets[:50]:
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            if total <= 1.005:
                print(f"Near: {total:.4f} {m.question[:60]} yes={yes_price} no={no_price}")
                counts += 1
    print("found", counts)

asyncio.run(check())
