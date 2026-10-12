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
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_misses = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        # debug print for first few
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60],
                'yes': opp.yes_price,
                'no': opp.no_price,
                'sum': opp.total_cost,
                'edge': opp.net_edge,
                'shares': opp.max_shares,
                'liq': m.liquidity
            })
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                # Use min price not first ask
                yes_price = float(min(yes_book.asks, key=lambda a: float(a['price']))['price'])
                no_price = float(min(no_book.asks, key=lambda a: float(a['price']))['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    print(f"markets {len(markets)} scan {scan_time:.1f}s")
    print('opps', len(opps))
    print('near', len(near_misses))
    for x in near_misses[:10]:
        print(x)

asyncio.run(scan())
