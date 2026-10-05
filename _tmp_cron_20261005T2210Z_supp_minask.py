import asyncio, logging, time, json
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
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.yes_price, opp.no_price, opp.max_shares, m.liquidity, m.question[:60]))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            ov = min(int(float(yes_book.asks[0]['size'])) if False else 0, 0)
            near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity)) if total <= 1.005 else None
    # recompute overlap properly for the band
    band = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            t = yp + np_
            if t <= 1.005:
                ya = min(yes_book.asks, key=lambda a: float(a['price']))
                na = min(no_book.asks, key=lambda a: float(a['price']))
                ov = min(int(float(ya['size'])), int(float(na['size'])))
                band.append((t, m.question[:50], yp, np_, m.liquidity, ov))
    band.sort()
    return len(markets), priced, opps, band, scan_time

markets_n, priced, opps, band, scan_time = asyncio.run(scan())
print(f"[min-ask supplement] {markets_n} markets ({priced} priced) in {scan_time:.1f}s")
print(f"BRACKETS (detector, net_edge>=margin): {len(opps)}")
for t, e, yp, np_, sh, liq, q in sorted(opps):
    print(f"  sum={t:.3f} edge={e:.4f} Yes@{yp:.3f} No@{np_:.3f} shares={sh} liq={liq} | {q}")
print(f"Near-misses (best-ask sum <= 1.005): {len(band)}")
for t, q, yp, np_, liq, ov in band[:15]:
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | ov={ov} liq={liq} | {q}")
if band:
    print(f"FLOOR: {band[0][0]:.3f}")
