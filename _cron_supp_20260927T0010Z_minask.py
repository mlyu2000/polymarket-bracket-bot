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
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.max_shares, m.liquidity, m.question[:60]))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            near.append((total, m.question[:50], yp, np_, m.liquidity))

    near.sort()
    print(f"[min-ask supplement] {len(markets)} markets, {priced} priced books, {scan_time:.1f}s")
    print(f"BRACKETS via detector: {len(opps)}")
    for t, e, s, liq, q in sorted(opps):
        print(f"  🔴 sum={t:.3f} edge={e:.4f} shares={s} liq={liq} | {q}")
    print("Top-8 min-ask sums:")
    for total, q, yp, np_, liq in near[:8]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"True floor (min sum across all priced): {near[0][0]:.3f}" if near else "no priced books")

asyncio.run(scan())
