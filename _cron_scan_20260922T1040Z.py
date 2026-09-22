import asyncio, logging, time, json, os
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
    near_misses_provided_asks0 = []
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
            paper.execute(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                # Correct floor: asks are DESC-sorted, use min() like detector.py
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((round(total, 4), m.question[:50], yes_price, no_price, m.liquidity))
                # Provided-script literal (asks[0]) for bug-demonstration
                y0 = float(yes_book.asks[0]['price'])
                n0 = float(no_book.asks[0]['price'])
                if y0 + n0 <= 1.005:
                    near_misses_provided_asks0.append((round(y0 + n0, 4), m.question[:50]))

    near_misses.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'near_misses_provided_asks0': near_misses_provided_asks0,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'runs')
os.makedirs(outdir, exist_ok=True)
outfile = os.path.join(outdir, f'cron_scan_{ts}.json')
with open(outfile, 'w') as f:
    json.dump({'ts_utc': ts, **result}, f, indent=2)

print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
print(f"[provided-script asks[0] literal count: {len(result['near_misses_provided_asks0'])}]")
print(f"[saved {outfile}]")
