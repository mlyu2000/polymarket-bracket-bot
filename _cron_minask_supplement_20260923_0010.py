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
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, m.question[:50]))
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                # correct best ask = min price (asks are DESC-sorted)
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    print(f"[min-ask supplement] {len(markets)} markets in {scan_time:.1f}s")
    print(f"detector-flagged (sum<1.00): {len(opps)}")
    for s, q in opps:
        print(f"  {s:.4f} | {q}")
    print(f"min-ask near-misses (<=1.005): {len(near_misses)}")
    for total, q, yp, np_, liq in near_misses[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
