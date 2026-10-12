import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    if not book or not book.asks:
        return None
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
    near_misses = []
    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.yes_price, opp.no_price, opp.max_shares, m.liquidity, m.question[:60]))
        ya = best_ask(yes_book)
        na = best_ask(no_book)
        if ya is not None and na is not None:
            total = ya + na
            sums.append(total)
            if 1.0 < total <= 1.005:
                near_misses.append((total, m.question[:50], ya, na, m.liquidity))

    near_misses.sort()
    print(f"[min-ask corrected] Scan: {len(markets)} markets in {scan_time:.1f}s")
    print(f"BRACKETS (min-ask sum < 1.00): {len(opps)}")
    for total, edge, yp, npv, sh, liq, q in sorted(opps):
        print(f"  RED {total:.4f} (edge={edge:.4f}) | Yes@{yp:.3f} No@{npv:.3f} | {sh} shares | liq={liq} | {q}")
    print(f"Near-misses (1.00 < best-ask sum <= 1.005): {len(near_misses)}")
    for total, q, yp, npv, liq in near_misses[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{npv:.3f} | liq={liq} | {q}")
    if sums:
        print(f"Floor of best-ask sums: {min(sums):.4f} | mean {sum(sums)/len(sums):.4f} | priced pairs: {len(sums)}")

asyncio.run(scan())
