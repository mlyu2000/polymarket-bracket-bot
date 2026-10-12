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
    near_misses = []      # provided method: asks[0] (known to be WORST ask)
    best_near = []        # supplement: min(best) ask both sides, <=1.005
    best_opps = []        # supplement: min-ask sum < 1.00 regardless of detector margin
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
            paper.execute(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            if 0 < yp < 1 and 0 < np_ < 1:
                priced += 1
                tot = round(yp + np_, 4)
                if tot <= 1.005:
                    best_near.append({'total': tot, 'q': m.question[:60], 'yes': yp, 'no': np_, 'liq': m.liquidity, 'shares': None})
                if tot < 1.00:
                    best_opps.append({'total': tot, 'q': m.question[:60], 'yes': yp, 'no': np_, 'liq': m.liquidity})

    near_misses.sort()
    best_near.sort(key=lambda d: d['total'])
    best_opps.sort(key=lambda d: d['total'])
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'priced': priced,
        'best_near': best_near,
        'best_opps': best_opps,
    }

result = asyncio.run(scan())
out = {
    'run_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'markets': result['markets'], 'priced': result['priced'],
    'scan_time': result['scan_time'],
    'detector_opps': result['opps'],
    'near_misses_asks0': result['near_misses'],
    'best_near_le1005': result['best_near'],
    'best_under_1': result['best_opps'],
}
fn = 'runs/cron_scan_' + time.strftime('%Y%m%dT%H%MZ', time.gmtime()) + '.json'
with open(fn, 'w') as f:
    json.dump(out, f, indent=2)

print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s  (saved {fn})")
print(f"✅ BRACKETS (detector, net edge >= margin): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 sum={o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']} | {o['q']}")
print(f"📊 Near-misses per prompt asks[0] logic (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
print(f"📉 Supplement — priced books: {result['priced']}")
print(f"🟢 sum<1.000 on best asks: {len(result['best_opps'])}")
for o in result['best_opps'][:5]:
    print(f"  🔴 {o['total']:.3f} | Yes@{o['yes']:.3f} No@{o['no']:.3f} | liq={o['liq']} | {o['q']}")
print(f"📊 Near-misses (≤1.005) on best asks: {len(result['best_near'])}")
for o in result['best_near'][:8]:
    print(f"  {o['total']:.3f} | Yes@{o['yes']:.3f} No@{o['no']:.3f} | liq={o['liq']} | {o['q']}")
if result['best_near']:
    print(f"Floor (lowest best-ask sum): {result['best_near'][0]['total']:.4f}")
