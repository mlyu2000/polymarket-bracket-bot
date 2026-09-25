# Supplement: near-misses computed with BEST asks (min), matching detector.py logic.
# The provided cron script uses asks[0] which is DESC-sorted (=worst ask ~0.999) and always reports 0.
import asyncio, json, logging, time
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

    priced = 0
    opps = []
    near_misses = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({'sum': opp.total_cost, 'edge': opp.net_edge, 'shares': opp.max_shares, 'q': m.question[:60]})
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            priced += 1
            if total <= 1.005:
                near_misses.append([round(total, 4), m.question[:50], yes_price, no_price, m.liquidity])

    near_misses.sort()
    opps.sort(key=lambda o: o['sum'])
    return {'ts': '2026-09-25T0426Z', 'markets': len(markets), 'priced': priced,
            'scan_time_s': round(scan_time, 1), 'brackets': opps,
            'best_floor': (near_misses[0] if near_misses else None),
            'near_misses_bestask': near_misses}

r = asyncio.run(scan())
with open('runs/cron_scan_20260925T0426Z.json', 'w') as f:
    json.dump(r, f)
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(r) + '\n')
print(f"priced={r['priced']} floor={r['best_floor'][0] if r['best_floor'] else None} near<=1.005={len(r['near_misses_bestask'])} brackets={len(r['brackets'])}")
for nm in r['near_misses_bestask'][:8]:
    print(f"  {nm[0]:.3f} | Yes@{nm[2]:.3f} No@{nm[3]:.3f} | liq={nm[4]:.0f} | {nm[1]}")
