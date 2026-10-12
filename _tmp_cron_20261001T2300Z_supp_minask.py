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
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        priced += 1
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        rows.append((ya + na, m.question[:55], ya, na, m.liquidity))

    rows.sort()
    print(f"Markets with priced books: {priced}")
    print(f"BEST-ASK floor sum: {rows[0][0]:.4f}" if rows else "no priced rows")
    print("Top 8 closest to <1.00 (best asks):")
    for s, q, ya, na, liq in rows[:8]:
        print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    under = [r for r in rows if r[0] < 1.0]
    print(f"TRUE BRACKETS (best-ask sum<1.00): {len(under)}")
    for s, q, ya, na, liq in under:
        print(f"  🟢 {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(supp())
