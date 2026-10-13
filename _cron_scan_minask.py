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

    bands = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            continue
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        # min(all asks) — asks are DESC-sorted; asks[0] is the worst price
        yes_price = min(float(a['price']) for a in yes_book.asks)
        no_price = min(float(a['price']) for a in no_book.asks)
        total = yes_price + no_price
        bands.append((total, m.question[:55], yes_price, no_price, m.liquidity))

    bands.sort()
    return {
        'markets': len(markets),
        'bands': bands,
        'scan_time': scan_time,
    }

r = asyncio.run(scan())
print(f"Scan: {r['markets']} markets in {r['scan_time']:.1f}s")
for th in (1.00, 1.005, 1.010, 1.020, 1.030, 1.050):
    n = sum(1 for b in r['bands'] if b[0] <= th)
    print(f"band <= {th:.3f}: n={n}")
print("Top 12 tightest (min-ask):")
for total, q, yp, np, liq in r['bands'][:12]:
    print(f"  {total:.4f} | Yes@{yp:.4f} No@{np:.4f} | liq={liq} | {q}")
