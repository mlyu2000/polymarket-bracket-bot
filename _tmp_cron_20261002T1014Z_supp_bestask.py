import asyncio, logging, time
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
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # asks are DESC-sorted; best ask = min price
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np, m.question[:50], yp, np, m.liquidity))
    rows.sort()
    print(f"priced={len(rows)}/{len(markets)}  floor={rows[0][0]:.3f} (best-ask basis)")
    print(f"brackets (<1.00): {sum(1 for r in rows if r[0] < 1.00)}")
    print(f"near-misses best-ask (<=1.005): {sum(1 for r in rows if r[0] <= 1.005)}")
    for total, q, yp, np, liq in rows[:5]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(supp())
