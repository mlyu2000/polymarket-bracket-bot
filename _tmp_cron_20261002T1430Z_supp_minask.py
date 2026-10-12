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

    true_brackets = []   # best-ask sum < 1.00 (detector-criteria misses would be bugs)
    near_misses_min = [] # best-ask sum <= 1.005
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            true_brackets.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60], m.liquidity))
            continue
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            total = ya + na
            if total < 1.0:
                true_brackets.append((total, 0.99999, 0, m.question[:60], m.liquidity))
            elif total <= 1.005:
                near_misses_min.append((total, m.question[:50], ya, na, m.liquidity))
    true_brackets.sort()
    near_misses_min.sort()
    print(f"min-ask floor scan: {priced}/{len(markets)} priced in {scan_time:.1f}s")
    print(f"TRUE BRACKETS (best-ask sum < 1.00): {len(true_brackets)}")
    for t, e, s, q, liq in true_brackets[:10]:
        print(f"  {t:.4f} | liq={liq} | {q}")
    print(f"NEAR-MISSES best-ask (<=1.005): {len(near_misses_min)}")
    for total, q, yp, np_, liq in near_misses_min[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    # overall floor
    floors = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            floors.append((min(float(a['price']) for a in yb.asks) + min(float(a['price']) for a in nb.asks), m.question[:50]))
    floors.sort()
    print("GLOBAL FLOOR top5:")
    for t, q in floors[:5]:
        print(f"  {t:.4f} | {q}")

asyncio.run(scan())
