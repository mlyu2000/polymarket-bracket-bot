import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging = __import__('logging')
logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()

    import time
    t0 = time.time()
    markets = await api.fetch_active_markets()
    print(f"Markets fetched: {len(markets)}")
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0
    print(f"Books fetched: {len(all_books)}")
    
    opps = []
    near_misses = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        # Use best ask
        yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
        no_ask = min(no_book.asks, key=lambda a: float(a['price']))
        yes_price = float(yes_ask['price'])
        no_price = float(no_ask['price'])
        total = yes_price + no_price
        if total < 1.0:
            opps.append((m.question[:60], total, yes_price, no_price))
        elif total <= 1.005:
            near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))
    
    near_misses.sort()
    print(f"🔍 Scan: {len(markets)} markets in {scan_time:.1f}s")
    print(f"✅ BRACKETS (sum < 1.00): {len(opps)}")
    for q, s, yp, np in opps:
        print(f"  {s:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
    print(f"📊 Near-misses (≤1.005): {len(near_misses)}")
    for total, q, yp, np, liq in near_misses[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")

asyncio.run(scan())
