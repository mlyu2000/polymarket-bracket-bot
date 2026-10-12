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
    dt = time.time() - t0

    rows = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        if total < 1.0:
            brackets.append((total, m.question[:60], yp, np_, m.liquidity))
        elif total <= 1.005:
            rows.append((total, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    brackets.sort()
    print(f"min-ask check: {len(markets)} markets in {dt:.1f}s")
    print(f"TRUE BRACKETS (best-ask sum < 1.00): {len(brackets)}")
    for total, q, yp, np_, liq in brackets[:10]:
        print(f"  sum={total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"NEAR-MISS (sum in [1.00, 1.005]): {len(rows)}")
    for total, q, yp, np_, liq in rows[:10]:
        print(f"  sum={total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    # floor across all priced markets
    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            s = min(float(a['price']) for a in yes_book.asks) + min(float(a['price']) for a in no_book.asks)
            sums.append(s)
    if sums:
        print(f"priced={len(sums)} floor={min(sums):.4f}")

asyncio.run(scan())
