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
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        if m.liquidity <= 0:
            continue
        priced += 1
        # True best ask = min (asks list is DESC-sorted)
        yes_best = min(float(a['price']) for a in yes_book.asks)
        no_best = min(float(a['price']) for a in no_book.asks)
        rows.append((yes_best + no_best, m.question[:55], yes_best, no_best, m.liquidity))
    rows.sort()
    print(f"priced markets (liq>0): {priced}")
    lt1 = [r for r in rows if r[0] < 1.0]
    print(f"true best-ask brackets (sum<1.0): {len(lt1)}")
    for total, q, yp, np, liq in lt1:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    le1005 = [r for r in rows if r[0] <= 1.005]
    print(f"true best-ask near-misses (<=1.005): {len(le1005)}")
    print("top-5 lowest sums (min-ask basis):")
    for total, q, yp, np, liq in rows[:5]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(supp())
