import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging = __import__('logging')
logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    print(f"Fetched {len(markets)} markets in {time.time()-t0:.1f}s")
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0
    opps = []
    near_misses = []
    for i,(m, (yes_book, no_book)) in enumerate(zip(markets, all_books)):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
            print(f"OPP FOUND: {m.question[:60]} sum={opp.total_cost}")
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))
    print(f"opps={len(opps)} near={len(near_misses)} scan_time={scan_time:.1f}")
    for total,q,yp,np,liq in near_misses[:10]:
        print(f" near {total:.3f} {q}")

asyncio.run(scan())
