import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    # lower liquidity for near misses
    Config.MIN_LIQUIDITY_USDC = 0
    t0 = time.time()
    markets = await api.fetch_active_markets(limit=500)
    print(f"markets fetched {len(markets)} in {time.time()-t0:.1f}s")
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    opps = []
    near = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        # find best ask by price not index
        yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
        no_ask = min(no_book.asks, key=lambda a: float(a['price']))
        yes_price = float(yes_ask['price'])
        no_price = float(no_ask['price'])
        total = yes_price + no_price
        if total <= 1.0:
            opps.append((total, m.question[:80], yes_price, no_price, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:80], yes_price, no_price, m.liquidity))
    opps.sort()
    near.sort()
    print(f"Brackets <=1.00: {len(opps)}")
    for o in opps[:10]:
        print(o)
    print(f"Near misses <=1.005: {len(near)}")
    for n in near[:20]:
        print(n)

asyncio.run(scan())
