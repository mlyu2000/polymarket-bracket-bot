import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def f():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=10)
    for m in markets:
        print("market", m.liquidity, m.question[:60])
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes, no = books[0]
        if not yes or not no:
            print(" no books")
            continue
        opp = detector.detect(m, yes, no)
        if opp:
            print(" FOUND", opp.total_cost)
        else:
            if yes.asks and no.asks:
                yprice = min(float(a['price']) for a in yes.asks)
                nprice = min(float(a['price']) for a in no.asks)
                total = yprice+nprice
                print(" total", total)

asyncio.run(f())
