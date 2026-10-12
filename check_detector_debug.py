import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=20)
    detector = BracketDetector()
    count = 0
    for m in markets:
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            print('FOUND', opp.total_cost, m.question[:60])
            count += 1
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                if total <= 1.005:
                    print('NEAR', total, yes_price, no_price, m.question[:60])
    print('Total found', count)

asyncio.run(f())
