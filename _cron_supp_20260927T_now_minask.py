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

    brackets = []
    near = []
    priced = 0
    best = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        priced += 1
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        if best is None or total < best[0]:
            best = (total, m.question[:60], ya, na, m.liquidity)
        if total < 1.00:
            brackets.append((total, m.question[:60], ya, na, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:60], ya, na, m.liquidity))

    near.sort()
    brackets.sort()
    return dict(markets=len(markets), priced=priced, scan_time=scan_time,
                brackets=brackets, near=near, best=best)

r = asyncio.run(scan())
print(f"[min-ask corrected scan] {r['priced']}/{r['markets']} markets priced in {r['scan_time']:.1f}s")
print(f"BRACKETS min-ask sum<1.00: {len(r['brackets'])}")
for t, q, yp, np_, liq in r['brackets'][:10]:
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"Near-misses min-ask <=1.005: {len(r['near'])}")
for t, q, yp, np_, liq in r['near'][:10]:
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"BEST floor: {r['best'][0]:.3f} | Yes@{r['best'][2]:.3f} No@{r['best'][3]:.3f} | liq={r['best'][4]} | {r['best'][1]}")
