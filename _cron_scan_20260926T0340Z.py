# Cron scan 2026-09-26: user-provided block (asks[0] near-misses, known to report 0)
# + corrected min-ask supplement matching detector.py, persisted to runs/ + results/ + git.
import asyncio, json, logging, time
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
    near_misses = []          # asks[0] version (user-provided spec)
    near_misses_best = []     # min-ask version (correct, matches detector)
    priced = 0
    paper_trades = []
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
            try:
                paper_trades.append(paper.execute(opp))
            except Exception as e:
                paper_trades.append({'error': str(e)})
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            # asks[0] (worst ask, DESC-sorted) per user script
            y0 = float(yes_book.asks[0]['price']); n0 = float(no_book.asks[0]['price'])
            if y0 + n0 <= 1.005:
                near_misses.append((y0 + n0, m.question[:50], y0, n0, m.liquidity))
            # min-ask (true best)
            ym = min(float(a['price']) for a in yes_book.asks)
            nm = min(float(a['price']) for a in no_book.asks)
            if ym + nm <= 1.005:
                near_misses_best.append((round(ym + nm, 4), m.question[:50], ym, nm, m.liquidity))

    near_misses.sort()
    near_misses_best.sort()
    return {
        'ts': time.strftime('%Y-%m-%dT%H%MZ', time.gmtime()),
        'markets': len(markets), 'priced': priced, 'scan_time': scan_time,
        'opps': opps, 'paper_trades': len(paper_trades),
        'near_misses_asks0': near_misses, 'near_misses_bestask': near_misses_best,
    }

r = asyncio.run(scan())
with open(f"runs/cron_scan_{r['ts']}.json", 'w') as f:
    json.dump(r, f, default=str)
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(r, default=str) + '\n')

print(f"🔍 Scan: {r['markets']} markets in {r['scan_time']:.1f}s ({r['priced']} priced)")
print(f"✅ BRACKETS (sum < 1.00): {len(r['opps'])}")
for o in r['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses asks[0] (<=1.005): {len(r['near_misses_asks0'])}")
for total, q, yp, np_, liq in r['near_misses_asks0'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
print(f"📊 Near-misses best-ask (<=1.005): {len(r['near_misses_bestask'])}")
for total, q, yp, np_, liq in r['near_misses_bestask'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
