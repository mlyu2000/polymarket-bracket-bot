import asyncio, logging, time, json, collections
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

    rows = []
    structural = collections.Counter()
    for m, (yes_book, no_book) in zip(markets, all_books):
        ya = yes_book.asks if yes_book else None
        na = no_book.asks if no_book else None
        if ya and na:
            structural['two_sided'] += 1
            yp = min(float(a['price']) for a in ya)
            np_ = min(float(a['price']) for a in na)
            rows.append((yp + np_, m.question, yp, np_, m.liquidity))
        elif ya and not na:
            structural['yes_only'] += 1
        elif na and not ya:
            structural['no_only'] += 1
        else:
            structural['empty'] += 1

    # detector-based bracket count (authoritative, uses min + depth)
    brackets = 0
    for m, (yb, nb) in zip(markets, all_books):
        if detector.detect(m, yb, nb):
            brackets += 1

    rows.sort()
    return {
        'markets': len(markets),
        'scan_time': scan_time,
        'brackets': brackets,
        'structural': dict(structural),
        'lowest': rows[:12],
        'le_098': [r for r in rows if r[0] <= 0.98],
        'le_1000': [r for r in rows if r[0] <= 1.000],
        'le_1005': [r for r in rows if r[0] <= 1.005],
    }

result = asyncio.run(scan())
print(f"🔍 {result['markets']} markets in {result['scan_time']:.1f}s | brackets(detector,min+depth)={result['brackets']}")
print(f"🏗 structural: {result['structural']}")
print(f"📉 Floor counts: ≤0.98={len(result['le_098'])} ≤1.000={len(result['le_1000'])} ≤1.005={len(result['le_1005'])}")
print("📊 Lowest min-ask sums (true floor):")
for total, q, yp, np_, liq in result['lowest']:
    print(f"  {total:.4f} | Y@{yp:.3f} N@{np_:.3f} | liq={liq} | {q[:70]}")

with open('runs/_tmp_cron_20261012T114614Z_supp_data.json', 'w') as f:
    json.dump({'structural': result['structural'],
               'lowest': [(t, q, yp, n, l) for t, q, yp, n, l in result['lowest']],
               'le_098': [(t, q, yp, n, l) for t, q, yp, n, l in result['le_098']],
               'le_1000': [(t, q, yp, n, l) for t, q, yp, n, l in result['le_1000']]}, f, indent=2, default=str)
print("saved: runs/_tmp_cron_20261012T114614Z_supp_data.json")
