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
    priced = 0
    best_total = 10.0
    tier_hist = {}
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
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                priced += 1
                # CLOB /book asks are DESC-sorted: asks[0] is the WORST ask.
                # Use the BEST (lowest) ask on each side.
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                best_total = min(best_total, total)
                tier = round(total * 1000) / 1000
                tier_hist.setdefault(tier, []).append((round(total, 3), m.question[:50], yes_price, no_price, m.liquidity))
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    tiers = {k: sorted(v)[:5] for k, v in sorted(tier_hist.items())[:6]}
    return {
        'markets': len(markets),
        'priced': priced,
        'opps': opps,
        'near_misses': near_misses,
        'best_total': best_total,
        'tiers': tiers,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"Scan: {result['markets']} markets ({result['priced']} priced) in {result['scan_time']:.1f}s")
print(f"BRACKETS (net edge, best-ask): {len(result['opps'])}")
for o in result['opps']:
    print(f"  RED {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']:.0f} | {o['q']}")
print(f"Near-misses (<=1.005): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
print(f"Best total across all priced markets: {result['best_total']:.3f}")
print("Tier history (lowest 6 tiers):")
for tier, members in result['tiers'].items():
    print(f"  [{tier:.3f}] n={len(members)}")
    for t, q, yp, np_, liq in members:
        print(f"    {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
with open('_tmp_cron_20261010T015751Z_supp_data.json', 'w') as f:
    json.dump(result, f, default=str)
