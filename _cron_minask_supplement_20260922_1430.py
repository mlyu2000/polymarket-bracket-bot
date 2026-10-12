import asyncio, logging, time, json, datetime
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

    brackets, near, priced = [], [], 0
    best = 9.9
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            brackets.append({'sum': opp.total_cost, 'edge': opp.net_edge,
                             'yes': opp.yes_price, 'no': opp.no_price,
                             'shares': opp.max_shares, 'q': m.question[:60]})
            continue
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np = min(float(a['price']) for a in nb.asks)
            total = yp + np
            priced += 1
            best = min(best, total)
            if total <= 1.005:
                near.append((round(total, 6), m.question[:60], yp, np, m.liquidity))
    near.sort()
    return {'markets': len(markets), 'priced': priced, 'scan_time': scan_time,
            'best_min_sum': best, 'brackets': brackets, 'near': near}

r = asyncio.run(scan())
print(f"min-ask supplement: {r['markets']} markets, {r['priced']} priced, {r['scan_time']:.1f}s")
print(f"best min-ask sum: {r['best_min_sum']:.4f}")
print(f"brackets: {len(r['brackets'])}")
for b in r['brackets']:
    print(f"  {b['sum']:.4f} edge={b['edge']:.4f} yes={b['yes']:.3f} no={b['no']:.3f} | {b['q']}")
print(f"near (<=1.005): {len(r['near'])}")
for t, q, yp, np, liq in r['near'][:10]:
    print(f"  {t:.4f} | yes@{yp:.3f} no@{np:.3f} | liq={liq:.0f} | {q}")

ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
with open(f'runs/cron_scan_{ts}.json', 'w') as f:
    json.dump({'ts': ts, 'method': 'min-ask', 'markets': r['markets'], 'priced': r['priced'],
               'scan_seconds': r['scan_time'], 'best_min_sum': r['best_min_sum'],
               'brackets': r['brackets'], 'near_le_1005': r['near']}, f, indent=1)
print(f"saved runs/cron_scan_{ts}.json")
