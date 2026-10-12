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
    near = []
    priced = 0
    floor = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            if floor is None or total < floor[0]:
                floor = (total, m.question[:50], yp, np_, m.liquidity)
            if 0 < total <= 1.005:
                near.append((total, m.question[:50], yp, np_, m.liquidity))

    near.sort()
    return markets, opps, near, floor, priced, scan_time

markets, opps, near, floor, priced, scan_time = asyncio.run(scan())
print(f"[min-ask pass] {len(markets)} markets ({priced} priced) in {scan_time:.1f}s")
print(f"BRACKETS via detector: {len(opps)}")
for o in opps:
    print(f"  sum={o.total_cost:.4f} edge={o.net_edge:.4f} Yes@{o.yes_price:.3f} No@{o.no_price:.3f} shares={o.max_shares}")
print(f"Near-misses (min-ask sum <= 1.005): {len(near)}")
for total, q, yp, np_, liq in near[:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if floor:
    print(f"FLOOR (lowest min-ask sum): {floor[0]:.4f} | Yes@{floor[2]:.3f} No@{floor[3]:.3f} | liq={floor[4]} | {floor[1]}")
