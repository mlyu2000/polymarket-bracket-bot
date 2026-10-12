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
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        priced += 1
        # CLOB /book returns asks DESC-sorted; best ask = min price
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))

    rows.sort()
    print(f"priced markets (best-ask floor): {priced}/{len(markets)}")
    brackets = [r for r in rows if r[0] < 1.0]
    near = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"sum<1.00 on best asks (true brackets): {len(brackets)}")
    for total, q, yp, np_, liq in brackets[:10]:
        print(f"  [BRACKET] {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"near-misses (1.000<=sum<=1.005) on best asks: {len(near)}")
    for total, q, yp, np_, liq in near[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    if rows:
        print(f"true floor (min sum of best asks): {rows[0][0]:.4f}")

asyncio.run(scan())
