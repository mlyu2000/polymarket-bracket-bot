import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    skipped = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            skipped += 1
            continue
        priced += 1
        # Best ask = MINIMUM price; CLOB returns asks in DESCENDING order,
        # so asks[0] is the WORST ask (this is why the verbatim near-miss
        # block always reports 0).
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        rows.append((yp + np_, yp, np_, m.question[:60], m.liquidity))

    rows.sort()
    print(f"priced={priced} skipped_no_best_ask={skipped}")
    if rows:
        print(f"FLOOR best-ask-sum = {rows[0][0]:.3f}")
        print("Top-10 lowest best-ask sums:")
        for total, yp, np_, q, liq in rows[:10]:
            print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
        nm = [r for r in rows if r[0] <= 1.005]
        lt1 = [r for r in rows if r[0] < 1.00]
        print(f"near-misses(best-ask, <=1.005): {len(nm)} | sum<1.000 raw: {len(lt1)}")

asyncio.run(scan())
