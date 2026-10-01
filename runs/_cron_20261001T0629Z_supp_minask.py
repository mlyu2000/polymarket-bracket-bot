import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        # asks are DESC-sorted in the CLOB book -> best ask = min()
        yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
        no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
        yp = float(yes_ask["price"]); np_ = float(no_ask["price"])
        rows.append((yp + np_, m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    print(f"priced markets: {len(rows)} / {len(markets)}")
    print(f"true floor (min-ask sum): {rows[0][0]:.3f}" if rows else "no priced markets")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"min-ask near-misses (<=1.005): {len(nm)}")
    for total, q, yp, np_, liq in nm[:8]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(supp())
