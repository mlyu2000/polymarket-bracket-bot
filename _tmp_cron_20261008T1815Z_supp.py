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
    sub_one = []
    near = []
    min_sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_best = min(float(a['price']) for a in yes_book.asks)
            no_best = min(float(a['price']) for a in no_book.asks)
            total = yes_best + no_best
            min_sums.append(total)
            row = (total, m.question[:50], yes_best, no_best, m.liquidity)
            if total <= 1.0:
                sub_one.append(row)
            elif total <= 1.005:
                near.append(row)

    sub_one.sort(); near.sort(); min_sums.sort()
    return {'markets': len(markets), 'priced': len(min_sums), 'opps': opps,
            'sub_one': sub_one, 'near': near,
            'min_sum': min_sums[0] if min_sums else None,
            'scan_time': scan_time}

result = asyncio.run(scan())
print(f"[supp min-ask] {result['markets']} markets ({result['priced']} priced) in {result['scan_time']:.1f}s")
print(f"[supp] best min-ask sum across all markets: {result['min_sum']:.4f}")
print(f"[supp] min-ask sum <= 1.00: {len(result['sub_one'])}")
for total, q, yp, np, liq in result['sub_one'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"[supp] near-misses 1.00<sum<=1.005: {len(result['near'])}")
for total, q, yp, np, liq in result['near'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
