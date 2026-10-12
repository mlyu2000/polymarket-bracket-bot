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
    floors = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60], 'yes': opp.yes_price, 'no': opp.no_price,
                'sum': opp.total_cost, 'edge': opp.net_edge,
                'shares': opp.max_shares, 'liq': m.liquidity
            })
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            floors.append(total)
            if 1.0 <= total <= 1.005:
                near_misses.append((total, m.question[:50], yp, np_, m.liquidity))

    near_misses.sort()
    floors.sort()
    return {'markets': len(markets), 'priced': priced, 'opps': opps,
            'near_misses': near_misses, 'floor': floors[0] if floors else None,
            'n_below_1': sum(1 for f in floors if f < 1.0),
            'scan_time': scan_time}

r = asyncio.run(scan())
print(f"BestAsk supplement: {r['markets']} markets ({r['priced']} priced) in {r['scan_time']:.1f}s")
print(f"BRACKETS (detector, sum < 1.00): {len(r['opps'])}")
for o in r['opps']:
    print(f"  RED sum={o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']} | {o['q']}")
print(f"True floor across priced markets: {r['floor']} | count(sum<1.0)={r['n_below_1']}")
print(f"Near-misses best-ask (1.00..1.005): {len(r['near_misses'])}")
for total, q, yp, np_, liq in r['near_misses'][:8]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
