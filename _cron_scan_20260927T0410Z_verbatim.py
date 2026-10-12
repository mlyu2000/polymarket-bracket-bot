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
    near_misses = []
    minask_rows = []
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
                # verbatim block (asks[0] — known buggy: asks are DESC-sorted)
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))
                # corrected min-ask computation
                ya = min(float(a['price']) for a in yes_book.asks)
                na = min(float(a['price']) for a in no_book.asks)
                minask_rows.append((ya + na, m.question[:55], ya, na, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'minask_rows': minask_rows,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")

rows = sorted(result['minask_rows'])
print(f"--- corrected min-ask floor (n={len(rows)}) ---")
for s, q, ya, na, liq in rows[:8]:
    print(f"  {s:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq:,.0f} | {q}")
br = [r for r in rows if r[0] < 1.0]
nr = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"min-ask BRACKETS sum<1.00: {len(br)} | near-misses 1.000-1.005: {len(nr)}")

import datetime
ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
with open(f'runs/cron_scan_{ts}.json', 'w') as f:
    json.dump({'ts': ts, 'markets': result['markets'], 'opps': result['opps'],
               'near_misses_verbatim': result['near_misses'],
               'minask_floor': rows[:20]}, f, indent=2)
