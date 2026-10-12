"""Min-ask supplement: near-miss floor using TRUE best asks (asks are DESC-sorted)."""
import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    return min(float(a['price']) for a in book.asks)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60], 'yes': opp.yes_price, 'no': opp.no_price,
                'sum': opp.total_cost, 'edge': opp.net_edge,
                'shares': opp.max_shares, 'liq': m.liquidity,
            })
        elif yes_book and no_book and yes_book.asks and no_book.asks:
            yp = best_ask(yes_book)
            np = best_ask(no_book)
            tot = yp + np
            priced += 1
            if tot <= 1.005:
                near.append((round(tot, 4), m.question[:55], yp, np, m.liquidity))
    near.sort()
    return {'markets': len(markets), 'priced': priced, 'opps': opps,
            'near': near, 'scan_time': scan_time}

r = asyncio.run(scan())
print(f"[min-ask] {r['markets']} markets ({r['priced']} priced) in {r['scan_time']:.1f}s")
print(f"[min-ask] BRACKETS: {len(r['opps'])}")
for o in r['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']}sh liq={o['liq']} | {o['q']}")
print(f"[min-ask] near-misses (≤1.005): {len(r['near'])}")
for tot, q, yp, np, liq in r['near'][:8]:
    print(f"  {tot:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
with open('runs/scan_20260924T064733Z_minask.json', 'w') as f:
    json.dump(r, f, indent=2, default=str)
