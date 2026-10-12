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
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60],
                'sum': opp.total_cost,
                'edge': opp.net_edge,
                'shares': opp.max_shares,
            })
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_ask = min(float(a['price']) for a in yes_book.asks)
                no_ask = min(float(a['price']) for a in no_book.asks)
                total = yes_ask + no_ask
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_ask, no_ask, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'priced': sum(1 for m, (yb, nb) in zip(markets, all_books) if yb and nb and yb.asks and nb.asks),
    }

result = asyncio.run(scan())
print(f"[minask] Scan: {result['markets']} markets ({result['priced']} priced) in {result['scan_time']:.1f}s")
print(f"[minask] BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  [BRACKET] {o['sum']:.3f} (edge={o['edge']:.4f}) | {o['shares']} shares | {o['q']}")
print(f"[minask] Near-misses (<=1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
