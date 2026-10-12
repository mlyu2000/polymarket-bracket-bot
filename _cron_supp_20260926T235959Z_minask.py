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
            opps.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60]))
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                # CORRECTED: best ask = min (asks are DESC-sorted from API)
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return {'markets': len(markets), 'opps': opps, 'near_misses': near_misses, 'scan_time': scan_time}

result = asyncio.run(scan())
print(f"[MIN-ASK CORRECTED] {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"BRACKETS: {len(result['opps'])}")
for s, e, sh, q in result['opps']:
    print(f"  {s:.3f} edge={e:.4f} shares={sh} | {q}")
print(f"Near-misses (<=1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
