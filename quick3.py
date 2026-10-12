import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def f():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
    yes, no = books[0]
    opp = detector.detect(m, yes, no)
    print("opp", opp)
    if yes and yes.asks:
        yprice = min(float(a['price']) for a in yes.asks)
        print("yprice", yprice)
    if no and no.asks:
        nprice = min(float(a['price']) for a in no.asks)
        print("nprice", nprice)

asyncio.run(f())
