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
    near_misses = []
    bestask_near = []
    best_floor = None
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
                # verbatim user-script near-miss check (asks[0])
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))
                # supplement: best-ask (min) totals - asks are DESC-sorted, asks[0] is worst
                byes = min(float(a['price']) for a in yes_book.asks)
                bno = min(float(a['price']) for a in no_book.asks)
                btotal = byes + bno
                priced += 1
                if best_floor is None or btotal < best_floor[0]:
                    best_floor = (btotal, m.question[:50], byes, bno, m.liquidity)
                if btotal <= 1.005:
                    bestask_near.append((btotal, m.question[:50], byes, bno, m.liquidity))

    near_misses.sort()
    bestask_near.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'bestask_near': bestask_near,
        'best_floor': best_floor,
        'priced': priced,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
print(f"📉 Best-ask floor: {result['best_floor'][0]:.4f} | Yes@{result['best_floor'][2]:.3f} No@{result['best_floor'][3]:.3f} | {result['best_floor'][1]}")
print(f"📊 Best-ask near-misses (≤1.005): {len(result['bestask_near'])} of {result['priced']} priced")
for total, q, yp, np_, liq in result['bestask_near'][:8]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")

# persist (git-persisted runs convention)
out = {
    'ts': '2026-09-24T2019Z',
    'markets': result['markets'],
    'priced': result['priced'],
    'scan_time_s': round(result['scan_time'], 1),
    'brackets': result['opps'],
    'near_misses_asks0': result['near_misses'],
    'near_misses_bestask': result['bestask_near'],
    'best_floor': result['best_floor'],
}
with open('runs/cron_scan_20260924T2019Z.json', 'w') as f:
    json.dump(out, f, indent=1)
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(out) + "\n")
print("SAVED runs/cron_scan_20260924T2019Z.json")
