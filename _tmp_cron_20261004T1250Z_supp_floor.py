import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        priced += 1
        best_yes = min(float(a['price']) for a in yb.asks)
        best_no = min(float(a['price']) for a in nb.asks)
        rows.append((best_yes + best_no, m.question[:60], best_yes, best_no, m.liquidity))

    rows.sort()
    print(f"priced books: {priced}")
    print("true best-ask floor (min over asks), closest 8:")
    for t, q, yp, np_, liq in rows[:8]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    brackets = [r for r in rows if r[0] < 1.0]
    print(f"true brackets (sum<1.00): {len(brackets)}")
    for t, q, yp, np_, liq in brackets:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(supp())
