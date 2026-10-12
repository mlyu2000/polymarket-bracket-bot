# Supplementary: near-misses using BEST asks (min price), since CLOB /book
# returns asks in descending order — asks[0] is the WORST ask (~0.999).
import asyncio, logging, json, time
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

    near = []
    priced = 0
    floor = None
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append((opp.total_cost, m.question[:60], opp.yes_price, opp.no_price, opp.net_edge, opp.max_shares))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            if floor is None or total < floor[0]:
                floor = (total, m.question[:60], yp, np_, m.liquidity)
            if 0 < total <= 1.005:
                near.append((total, m.question[:60], yp, np_, m.liquidity, opp is not None))

    near.sort()
    print(f"scan time: {scan_time:.1f}s | markets: {len(markets)} | priced: {priced}")
    if floor:
        print(f"global min sum(best asks): {floor[0]:.4f} | Yes@{floor[2]:.3f} No@{floor[3]:.3f} | {floor[1]}")
    print(f"detector-flagged brackets (best asks, net edge>=margin): {len(brackets)}")
    for b in sorted(brackets)[:10]:
        print(f"  🔴 sum={b[0]:.4f} | Yes@{b[2]:.3f} No@{b[3]:.3f} | edge={b[4]:.4f} | {b[5]} shares | {b[1]}")
    print(f"best-ask near-misses (<=1.005): {len(near)}")
    for t, q, yp, np_, liq, flagged in near[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | det={'YES' if flagged else 'no'} | {q}")
    return markets, priced, floor, near, brackets, scan_time

markets, priced, floor, near, brackets, scan_time = asyncio.run(scan())
ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
out = {
    'run': ts,
    'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'markets': len(markets),
    'priced': priced,
    'floor': floor[0] if floor else None,
    'floor_q': floor[1] if floor else None,
    'band_le_1005': len(near),
    'brackets_minask': len(brackets),
    'top10': [list(n) for n in near[:10]],
    'scan_time_s': round(scan_time, 1),
}
with open(f'runs/scan_{ts}.json', 'w') as f:
    json.dump(out, f, indent=1)
