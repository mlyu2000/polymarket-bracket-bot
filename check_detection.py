import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    print('markets', len(markets))
    opps = []
    for m in markets[:20]:
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            print('OPP', m.question[:60], opp.total_cost)
            opps.append(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
                no_ask = min(no_book.asks, key=lambda a: float(a['price']))
                yp = float(yes_ask['price'])
                np = float(no_ask['price'])
                total = yp + np
                if total <= 1.005:
                    print('NEAR', total, m.question[:60])
    print('done', len(opps))

asyncio.run(scan())
