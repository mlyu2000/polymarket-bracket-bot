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

    totals = []
    brackets_min = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        s = yp + np_
        totals.append((s, m.question[:55], yp, np_, m.liquidity))
        if s < 1.0:
            brackets_min.append((s, m.question[:55], yp, np_, m.liquidity))
    totals.sort()
    return markets, totals, brackets_min, scan_time

mkts, totals, brackets, dt = asyncio.run(scan())
print(f"min-ask supplement: {len(mkts)} markets in {dt:.1f}s, {len(totals)} priced")
print(f"BRACKETS via min-ask (sum < 1.00): {len(brackets)}")
for s, q, yp, np_, liq in sorted(brackets):
    print(f"  🔴 {s:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"Best 8 totals (min-ask):")
for s, q, yp, np_, liq in totals[:8]:
    flag = " <1.00!" if s < 1.0 else (" <=1.005" if s <= 1.005 else "")
    print(f"  {s:.3f}{flag} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
