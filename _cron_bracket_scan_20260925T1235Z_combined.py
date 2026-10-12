# Cron run 2026-09-25: verbatim user script + best-ask supplement (asks[0] near-miss bug known).
import asyncio, json, logging, subprocess, sys, time

VERBATIM = '''
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

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
    near_misses = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60],
                'yes': opp.yes_price,
                'no': opp.no_price,
                'sum': opp.total_cost,
                'edge': opp.net_edge,
                'shares': opp.max_shares,
                'liq': m.liquidity
            })
            paper_result = paper.execute(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"SCAN_MARKETS={result['markets']}")
print(f"SCAN_TIME={result['scan_time']:.1f}")
print(f"BRACKETS={len(result['opps'])}")
for o in result['opps']:
    print(f"BRACKET | {o['sum']:.3f} | edge={o['edge']:.4f} | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']} | {o['q']}")
print(f"NEAR_VERBATIM={len(result['near_misses'])}")

import json as _json
with open('/tmp/_cron_20260925_verbatim.json','w') as f:
    _json.dump(result, f)
'''

SUPPLEMENT = '''
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
    return {'ts': '2026-09-25T1235Z', 'markets': len(markets), 'priced': priced,
            'scan_time_s': round(scan_time, 1), 'brackets': opps,
            'best_floor': (near_misses[0] if near_misses else None),
            'near_misses_bestask': near_misses}

r = asyncio.run(scan())
with open('runs/cron_scan_20260925T1235Z.json', 'w') as f:
    json.dump(r, f)
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(r) + '\\n')
print(f"PRICED={r['priced']} FLOOR={r['best_floor'][0] if r['best_floor'] else None} NEAR={len(r['near_misses_bestask'])} BRACKETS={len(r['brackets'])}")
for nm in r['near_misses_bestask'][:10]:
    print(f"NEAR | {nm[0]:.4f} | Yes@{nm[2]:.3f} No@{nm[3]:.3f} | liq={nm[4]} | {nm[1]}")
'''

import os
os.makedirs('runs', exist_ok=True)
os.makedirs('results', exist_ok=True)

with open('/tmp/_cron_verbatim_20260925.py', 'w') as f:
    f.write(VERBATIM)

print('=== VERBATIM SCRIPT OUTPUT ===')
env = dict(os.environ, PYTHONPATH=os.getcwd())
p = subprocess.run([sys.executable, '/tmp/_cron_verbatim_20260925.py'], capture_output=True, text=True, timeout=600, env=env)
print(p.stdout)
if p.returncode != 0:
    print('STDERR:', p.stderr[-3000:], file=sys.stderr)
    sys.exit(p.returncode)

print('=== BEST-ASK SUPPLEMENT OUTPUT ===')
with open('/tmp/_cron_supp_20260925.py', 'w') as f:
    f.write(SUPPLEMENT)
p2 = subprocess.run([sys.executable, '/tmp/_cron_supp_20260925.py'], capture_output=True, text=True, timeout=600, env=env)
print(p2.stdout)
if p2.returncode != 0:
    print('STDERR:', p2.stderr[-3000:], file=sys.stderr)
    sys.exit(p2.returncode)
