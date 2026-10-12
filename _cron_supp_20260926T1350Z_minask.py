"""Supplement: same scan but near-misses use BEST asks (min), since CLOB
asks arrays are DESC-sorted and asks[0] is the worst ask."""
import asyncio, logging, time
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

    opps = []
    near_misses = []
    priced = 0
    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60], 'yes': opp.yes_price, 'no': opp.no_price,
                'sum': opp.total_cost, 'edge': opp.net_edge,
                'shares': opp.max_shares, 'liq': m.liquidity,
            })
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            priced += 1
            sums.append(total)
            if 1.000 < total <= 1.005 and m.liquidity > 0:
                near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets), 'priced': priced, 'opps': opps,
        'near_misses': near_misses, 'scan_time': scan_time,
        'floor': min(sums) if sums else None,
    }

result = asyncio.run(scan())
print(f"[supplement] {result['markets']} markets, {result['priced']} priced pairs, {result['scan_time']:.1f}s")
print(f"[supplement] true floor (min sum across priced): {result['floor']}")
print(f"[supplement] BRACKETS (detector, net_edge>=margin): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 sum={o['sum']:.4f} edge={o['edge']:.4f} Yes@{o['yes']:.3f} No@{o['no']:.3f} shares={o['shares']} liq={o['liq']} | {o['q']}")
print(f"[supplement] Near-misses via BEST asks (1.000<sum<=1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
