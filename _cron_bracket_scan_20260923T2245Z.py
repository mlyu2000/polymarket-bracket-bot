import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    # CLOB /book asks are DESC-sorted; true best ask = min price.
    # (cron-prompt's asks[0] is the WORST ask ~0.999 — known-broken since 2026-09-21;
    #  detector.py already fixed in commit 0a8e754)
    return float(min(book.asks, key=lambda a: float(a['price']))['price'])

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
    priced = 0
    floor = None
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
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yes_price = best_ask(yes_book)
            no_price = best_ask(no_book)
            total = yes_price + no_price
            if floor is None or total < floor:
                floor = total
            if total <= 1.005:
                near_misses.append((round(total, 4), m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'floor': round(floor, 4) if floor is not None else None,
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
with open('runs/cron_20260923T2245Z.json', 'w') as f:
    json.dump(result, f, indent=1)

print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s ({result['priced']} with two-sided asks, true floor sum={result['floor']})")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']} | {o['q']}")
print(f"📊 Near-misses (best-ask ≤1.005): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
