import asyncio
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=10)
    detector = BracketDetector()
    for m in markets:
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # find best ask by min price
            yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
            no_ask = min(no_book.asks, key=lambda a: float(a['price']))
            yp = float(yes_ask['price'])
            np = float(no_ask['price'])
            total = yp + np
            print(m.question[:80])
            print('  best asks:', yp, np, 'sum', total)
            print('  first asks:', float(yes_book.asks[0]['price']), float(no_book.asks[0]['price']))
            print()

asyncio.run(f())
