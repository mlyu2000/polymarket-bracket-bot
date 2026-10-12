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
    true_brackets_raw = []
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
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            if total < 1.0:
                true_brackets_raw.append((total, m.question[:50], yes_price, no_price, m.liquidity))
            elif total <= 1.005:
                near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    true_brackets_raw.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'opps': opps,
        'true_brackets_raw': true_brackets_raw,
        'near_misses': near_misses,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"Supp(min-ask): {result['markets']} markets, {result['priced']} priced, in {result['scan_time']:.1f}s")
print(f"Detector BRACKETS: {len(result['opps'])}")
for o in result['opps']:
    print(f"  >> sum={o['sum']:.3f} edge={o['edge']:.4f} Yes@{o['yes']:.3f} No@{o['no']:.3f} {o['shares']}sh liq={o['liq']} | {o['q']}")
print(f"Raw best-ask sum<1.00: {len(result['true_brackets_raw'])}")
for total, q, yp, np, liq in result['true_brackets_raw'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"Near-misses (best-ask sum in (1.00,1.005]): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
