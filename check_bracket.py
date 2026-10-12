import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def debug():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    print("Fetched", len(markets))
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    cnt = 0
    for m, (y,n) in zip(markets, books):
        if not y or not n:
            continue
        if not y.asks or not n.asks:
            continue
        yes_ask = min(y.asks, key=lambda a: float(a['price']))
        no_ask = min(n.asks, key=lambda a: float(a['price']))
        yes_price = float(yes_ask['price'])
        no_price = float(no_ask['price'])
        total = yes_price + no_price
        if total < 1.0:
            cnt += 1
            print("BRACKET!", total, m.question[:80])
    print("Total brackets <1.0:", cnt)

asyncio.run(debug())
