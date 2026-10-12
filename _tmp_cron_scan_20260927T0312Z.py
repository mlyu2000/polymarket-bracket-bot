import asyncio, logging, time, json
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
    near_misses_verbatim = []   # prompt's method: asks[0] (worst ask on DESC-sorted CLOB books -> always ~1.0)
    near_misses = []            # corrected: best ask = min price
    priced = 0
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
                priced += 1
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses_verbatim.append((total, m.question[:50], yes_price, no_price, m.liquidity))
                # best ask = min price (CLOB lists asks DESC-sorted; asks[0] is worst)
                ym = min(float(a['price']) for a in yes_book.asks)
                nm = min(float(a['price']) for a in no_book.asks)
                tmin = ym + nm
                if tmin <= 1.005:
                    near_misses.append((tmin, m.question[:50], ym, nm, m.liquidity))

    near_misses.sort()
    near_misses_verbatim.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'opps': opps,
        'near_misses': near_misses,
        'near_misses_verbatim': near_misses_verbatim,
        'scan_time': scan_time,
    }

ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
result = asyncio.run(scan())
print(f"SCAN_TS_UTC={ts}")
print(f"Scan: {result['markets']} markets ({result['priced']} with 2-sided asks) in {result['scan_time']:.1f}s")
print(f"BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  [{o['sum']:.3f}] (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']} | {o['q']}")
print(f"Near-misses best-ask (<=1.005): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"Near-misses verbatim asks[0] (<=1.005): {len(result['near_misses_verbatim'])}")
for total, q, yp, np_, liq in result['near_misses_verbatim'][:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

import os
os.makedirs('runs', exist_ok=True)
with open(f"runs/cron_scan_{ts.replace(':','')}.json", 'w') as f:
    json.dump({'scan_ts_utc': ts, **{k: (v if not isinstance(v, list) or k != 'near_misses_verbatim' else [list(x) for x in v]) for k, v in result.items()},
               'near_misses': [list(x) for x in result['near_misses']]}, f, indent=1, default=str)
print(f"saved runs/cron_scan_{ts.replace(':','')}.json")
