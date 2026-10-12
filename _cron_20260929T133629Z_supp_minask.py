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

    priced = 0
    best = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        priced += 1
        rec = (total, m.question[:60], yp, np, m.liquidity)
        if best is None or total < best[0]:
            best = rec
        if total < 1.0:
            print(f"  TRUE BRACKET {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={m.liquidity} | {m.question[:60]}")

    return {'markets': len(markets), 'priced': priced, 'best': best, 'scan_time': scan_time}

result = asyncio.run(scan())
print(f"[supp best-ask] {result['markets']} markets ({result['priced']} with both books) in {result['scan_time']:.1f}s")
if result['best']:
    total, q, yp, np, liq = result['best']
    print(f"[supp] lowest sum of best asks: {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
