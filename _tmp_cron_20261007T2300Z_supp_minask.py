import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # asks are DESC-sorted; best ask = min (matches detector.py logic)
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            rows.append((total, m.question[:60], yes_price, no_price, m.liquidity))
    rows.sort()
    return {'markets': len(markets), 'rows': rows, 'scan_time': scan_time}

result = asyncio.run(scan())
print(f"best-ask floor scan: {result['markets']} markets in {result['scan_time']:.1f}s")
brackets = [r for r in result['rows'] if r[0] < 1.0]
print(f"TRUE best-ask brackets (sum<1.0): {len(brackets)}")
for total, q, yp, np, liq in brackets[:10]:
    print(f"  sum={total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print("top-10 lowest sums (best asks):")
for total, q, yp, np, liq in result['rows'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
