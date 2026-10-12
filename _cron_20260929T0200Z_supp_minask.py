import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    brackets = []
    for m, (yb, nb) in zip(markets, books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        t = ya + na
        if t < 1.0:
            brackets.append((t, m.question[:60], ya, na, m.liquidity))
        rows.append((t, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    brackets.sort()
    print(f"markets_with_both_books={len(rows)}")
    print(f"TRUE_BEST_ASK_BRACKETS={len(brackets)}")
    for t, q, ya, na, liq in brackets:
        print(f"  BRACKET {t:.4f} Yes@{ya:.3f} No@{na:.3f} liq={liq} | {q}")
    print("FLOOR (best-ask sums, lowest 6):")
    for t, q, ya, na, liq in rows[:6]:
        print(f"  {t:.4f} Yes@{ya:.3f} No@{na:.3f} liq={liq} | {q}")

asyncio.run(supp())
