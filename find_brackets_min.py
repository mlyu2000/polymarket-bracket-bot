import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    found = []
    for m, (yes, no) in zip(markets, all_books):
        if not yes or not no or not yes.asks or not no.asks:
            continue
        yes_ask = min(yes.asks, key=lambda a: float(a['price']))
        no_ask = min(no.asks, key=lambda a: float(a['price']))
        total = float(yes_ask['price'])+float(no_ask['price'])
        if total < 1.0:
            found.append((total, m.question[:80], yes_ask, no_ask, m.liquidity))
    print('found', len(found))
    for f in found[:20]:
        print(f)

asyncio.run(scan())
