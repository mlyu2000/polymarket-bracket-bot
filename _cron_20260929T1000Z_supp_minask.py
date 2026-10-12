import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)

    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        priced += 1
        # min over all asks (asks are DESC-sorted in CLOB /book)
        y = min(float(a['price']) for a in yb.asks)
        n = min(float(a['price']) for a in nb.asks)
        rows.append((y + n, m.question[:50], y, n, m.liquidity))

    rows.sort()
    print(f"markets={len(markets)} priced_books={priced}")
    print(f"brackets min-ask (sum<1.00): {sum(1 for r in rows if r[0] < 1.0)}")
    print(f"near min-ask (<=1.005): {sum(1 for r in rows if r[0] <= 1.005)}")
    print("--- true floor (best 5 by min-ask sum) ---")
    for total, q, y, n, liq in rows[:5]:
        print(f"  {total:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")

asyncio.run(supp())
