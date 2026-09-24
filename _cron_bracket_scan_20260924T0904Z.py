"""Cron bracket scan 2026-09-24T0904Z — user-provided script plus min-ask near-miss supplement."""
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
    corrected_near = []
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
                # Supplement: best (min) asks, since CLOB asks list is DESC-sorted
                ym = min(float(a['price']) for a in yes_book.asks)
                nm = min(float(a['price']) for a in no_book.asks)
                tot = ym + nm
                if tot <= 1.005 and m.liquidity >= Config.MIN_LIQUIDITY_USDC:
                    corrected_near.append((tot, m.question[:50], ym, nm, m.liquidity))

    near_misses.sort()
    corrected_near.sort()
    # Overall min sum across all priced markets (floor tracking)
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'corrected_near': corrected_near,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
import json, os
ts = "20260924T0904Z"
PERSIST_DIR = "runs"
os.makedirs(PERSIST_DIR, exist_ok=True)
with open(os.path.join(PERSIST_DIR, f"scan_{ts}_combined.json"), "w") as f:
    json.dump({'run_ts_utc': ts, **{k: v for k, v in result.items() if k != 'corrected_near'},
               'near_misses': [list(x) for x in result['corrected_near']],
               'asks0_near': [list(x) for x in result['near_misses']],
               'floor': min([x[0] for x in result['corrected_near']], default=None)}, f, indent=1)
hist = os.path.join('results', 'cron_scan_history.jsonl')
with open(hist, "a") as f:
    f.write(json.dumps({'run_ts_utc': ts, 'markets': result['markets'], 'scan_time_s': round(result['scan_time'],1),
        'brackets': result['opps'], 'near_miss_count': len(result['corrected_near']),
        'near_misses_top': [{'sum': t, 'q': q, 'yes': y, 'no': n, 'liq': l} for t,q,y,n,l in result['corrected_near'][:10]],
        'floor': min([x[0] for x in result['corrected_near']], default=None)}) + "\n")
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005, asks[0] method): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
print(f"📊 Near-misses (≤1.005, best-ask/min method, liq>={Config.MIN_LIQUIDITY_USDC:.0f}): {len(result['corrected_near'])}")
for total, q, yp, np, liq in result['corrected_near'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
