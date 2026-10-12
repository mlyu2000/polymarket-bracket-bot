import asyncio, logging, time, json
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
    all_sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60], 'yes': opp.yes_price, 'no': opp.no_price,
                'sum': opp.total_cost, 'edge': opp.net_edge,
                'shares': opp.max_shares, 'liq': m.liquidity
            })
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            npr = min(float(a['price']) for a in no_book.asks)
            total = yp + npr
            all_sums.append(total)
            if 1.0 < total <= 1.005:
                near_misses.append((total, m.question[:50], yp, npr, m.liquidity))

    near_misses.sort()
    all_sums.sort()
    return {
        'markets': len(markets), 'opps': opps, 'near_misses': near_misses,
        'scan_time': scan_time,
        'priced': len(all_sums),
        'floor': all_sums[0] if all_sums else None,
    }

result = asyncio.run(scan())
print(f"[min-ask corrected] Scan: {result['markets']} markets ({result['priced']} priced) in {result['scan_time']:.1f}s")
print(f"Detector brackets: {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 sum={o['sum']:.3f} edge={o['edge']:.4f} Yes@{o['yes']:.3f} No@{o['no']:.3f} {o['shares']} shares | {o['q']}")
print(f"True floor (min best-ask sum): {result['floor']}")
print(f"Near-misses 1.00<sum<=1.005 (min best asks): {len(result['near_misses'])}")
for total, q, yp, npr, liq in result['near_misses'][:8]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")

with open('_tmp_cron_20261009T0930Z_supp_data.json', 'w') as f:
    json.dump({k: v for k, v in result.items()}, f, default=str)
