import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    near_min = []
    brackets_min = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets_min.append({'sum': opp.total_cost, 'edge': opp.net_edge, 'q': m.question[:60]})
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            if total <= 1.005:
                near_min.append((total, m.question[:50], yp, np_, m.liquidity))
    near_min.sort()
    floor = min((min(float(a['price']) for a in y.asks) + min(float(a['price']) for a in n.asks))
                for y, n in all_books if y and n and y.asks and n.asks)
    return {'markets': len(markets), 'priced': priced, 'brackets': brackets_min, 'near': near_min, 'floor': floor}

r = asyncio.run(scan())
print(json.dumps(r, default=str))
