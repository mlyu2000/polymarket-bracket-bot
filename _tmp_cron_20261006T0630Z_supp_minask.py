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
    min_sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, m.question[:60]))
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                # CORRECTED: asks are DESC-sorted; best ask = min()
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                min_sums.append((total, m.question[:50], yes_price, no_price, m.liquidity))
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    min_sums.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'min_sums': min_sums,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"[min-ask corrected] Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"[min-ask corrected] BRACKETS (detector): {len(result['opps'])}")
for s, e, q in sorted(result['opps']):
    print(f"  🔴 sum={s:.3f} edge={e:.4f} | {q}")
print(f"[min-ask corrected] Near-misses (min-ask sum <=1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:8]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print("[min-ask corrected] Top-10 lowest true sums:")
for total, q, yp, np, liq in result['min_sums'][:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
