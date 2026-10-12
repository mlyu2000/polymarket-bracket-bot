import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def scan_all():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    # Use a small sample with lower liquidity to find brackets
    # Temporarily override config values for test
    original_max = Config.MAX_MARKETS_PER_SCAN
    original_min_liq = Config.MIN_LIQUIDITY_USDC
    # Can't mutate class vars easily, so fetch more markets
    markets = await api.fetch_active_markets(limit=200)
    print(f"Markets fetched: {len(markets)}")
    opps = []
    near = []
    for m in markets:
        if m.liquidity < 100:
            continue
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if not yes_book or not no_book:
            continue
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        else:
            # check near miss
            if yes_book.asks and no_book.asks:
                yes_asks = [float(a['price']) for a in yes_book.asks]
                no_asks = [float(a['price']) for a in no_book.asks]
                min_yes = min(yes_asks)
                min_no = min(no_asks)
                total = min_yes + min_no
                if total <= 1.005:
                    near.append((total, m.question[:60], min_yes, min_no, m.liquidity))
    print(f"Brackets found: {len(opps)}")
    for o in opps:
        print(f"  sum={o.total_cost:.3f} edge={o.net_edge:.4f} | {o.market.question[:60]}")
    print(f"Near misses: {len(near)}")
    for t,q,yp,np,liq in sorted(near)[:10]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")

asyncio.run(scan_all())
