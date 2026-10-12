"""Supplement: near-misses using BEST ask (min price), matching detector.py logic."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_misses = []
    floor = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks and m.liquidity > 0:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            if floor is None or total < floor[0]:
                floor = (total, m.question[:50], yp, np_, m.liquidity)
            if 1.00 < total <= 1.005:
                near_misses.append((total, m.question[:50], yp, np_, m.liquidity))

    near_misses.sort()
    print(f"🔍 Supp scan (best-ask): {len(markets)} markets in {scan_time:.1f}s")
    print(f"✅ BRACKETS (detector, sum<1.00 after guards): {len(opps)}")
    for o in opps:
        print(f"  🔴 sum={o.total_cost:.3f} edge={o.net_edge:.4f} | Yes@{o.yes_price:.3f} No@{o.no_price:.3f} | {o.max_shares} shares | {o.market_id if hasattr(o,'market_id') else ''}")
    print(f"📊 Near-misses best-ask (1.00 < sum <= 1.005): {len(near_misses)}")
    for total, q, yp, np_, liq in near_misses[:8]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
    if floor:
        print(f"⌊ Global best-ask floor: sum={floor[0]:.3f} | Yes@{floor[2]:.3f} No@{floor[3]:.3f} | {floor[1]}")

asyncio.run(scan())
