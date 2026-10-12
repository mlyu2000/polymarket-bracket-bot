import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    print('markets', len(markets))
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0
    opps = []
    near_misses = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
                no_ask = min(no_book.asks, key=lambda a: float(a['price']))
                yes_price = float(yes_ask['price'])
                no_price = float(no_ask['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))
    near_misses.sort()
    print('scan_time', scan_time)
    print('opps', len(opps))
    print('near', len(near_misses))
    for n in near_misses[:10]:
        print(n)

asyncio.run(scan())
