import asyncio, logging, json, time
from datetime import datetime, timezone
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

RUN = "20261006T0949Z"

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_verbatim = []   # verbatim asks[0] method (known biased: asks[0]=worst ask)
    top = []             # true best-ask (min) sums
    brackets_minask = 0
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({'q': m.question[:60], 'yes': opp.yes_price, 'no': opp.no_price,
                         'sum': opp.total_cost, 'edge': opp.net_edge,
                         'shares': opp.max_shares, 'liq': m.liquidity})
            paper.execute(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # verbatim near-miss method (asks[0])
            y0 = float(yes_book.asks[0]['price']); n0 = float(no_book.asks[0]['price'])
            if y0 + n0 <= 1.005:
                near_verbatim.append((y0 + n0, m.question[:50], y0, n0, m.liquidity))
            # true best-ask
            yp = min(float(a['price']) for a in yes_book.asks)
            npp = min(float(a['price']) for a in no_book.asks)
            total = round(yp + npp, 6)
            priced += 1
            if total < 1.00:
                brackets_minask += 1
            top.append({'sum': total, 'q': m.question[:60], 'yes': yp, 'no': npp, 'liq': m.liquidity})
    near_verbatim.sort()
    top.sort(key=lambda d: d['sum'])
    band = [t for t in top if 1.0 < t['sum'] <= 1.005]
    return {
        'markets': len(markets), 'priced': priced,
        'scan_time': scan_time, 'opps': opps, 'near_verbatim': near_verbatim,
        'floor': top[0]['sum'] if top else None,
        'brackets_minask': brackets_minask, 'band': len(band),
        'top': top[:8], 'band_entries': band,
    }

r = asyncio.run(scan())

run_json = {
    'markets': r['markets'], 'priced': r['priced'], 'floor': r['floor'],
    'brackets_minask': r['brackets_minask'], 'band_minask': r['band'],
    'top': r['top'],
}
latest_json = dict(run_json)
latest_json['run'] = RUN
latest_json['ts'] = datetime.now(timezone.utc).isoformat()
latest_json['scan_time_s'] = round(r['scan_time'], 1)
latest_json['brackets_detector'] = len(r['opps'])
latest_json['near_misses_verbatim_asks0'] = len(r['near_verbatim'])
latest_json['opps'] = r['opps']
floor_json = {
    'run': RUN, 'markets': r['markets'], 'brackets_minask': r['brackets_minask'],
    'band_1.000_1.005': r['band'], 'floor': r['floor'], 'priced': r['priced'],
    'top': r['top'], 'band_entries': r['band_entries'],
}
hist = {
    'ts': "2026-10-06T09:49Z",
    'markets': r['markets'], 'scan_time_s': round(r['scan_time'], 1),
    'brackets': len(r['opps']), 'brackets_true_minask': r['brackets_minask'],
    'near_misses_minask': r['band'], 'best_ask_floor': r['floor'],
    'priced_markets': r['priced'],
}

with open(f'runs/scan_{RUN}.json', 'w') as f:
    json.dump(run_json, f, indent=1)
with open('runs/scan_latest.json', 'w') as f:
    json.dump(latest_json, f, indent=1)
with open('runs/scan_latest_floor.json', 'w') as f:
    json.dump(floor_json, f, indent=1)
with open('runs/scan_history.jsonl', 'a') as f:
    f.write(json.dumps(hist) + "\n")
with open('runs/scan_latest.out', 'w') as f:
    f.write(f"Scan: {r['markets']} markets in {r['scan_time']:.1f}s\n")
    f.write(f"BRACKETS (detector, net_edge>=margin): {len(r['opps'])}\n")
    f.write(f"Near-misses verbatim asks[0] (<=1.005): {len(r['near_verbatim'])}\n")
    f.write(f"Min-ask floor: {r['floor']} over {r['priced']} priced markets; brackets(sum<1.00)={r['brackets_minask']}; band<=1.005={r['band']}\n")

print(f"[persist] runs/scan_{RUN}.json + latest + floor + history + out written")
print(f"[persist] markets={r['markets']} priced={r['priced']} floor={r['floor']} brackets_minask={r['brackets_minask']} band={r['band']} detector_opps={len(r['opps'])} near_asks0={len(r['near_verbatim'])}")
print("[persist] top entries:")
for t in r['top']:
    print(f"  {t['sum']:.4f} | Yes@{t['yes']:.3f} No@{t['no']:.3f} | liq={t['liq']} | {t['q']}")
