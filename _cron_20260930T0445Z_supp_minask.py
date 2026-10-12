import asyncio, logging, time
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
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            y = min(float(a['price']) for a in yb.asks)
            n = min(float(a['price']) for a in nb.asks)
            rows.append((y + n, m.question[:60], y, n, m.liquidity))
    rows.sort()
    print(f"priced={priced}/{len(markets)} true_floor={rows[0][0]:.3f}" if rows else "no priced books")
    for r in rows[:8]:
        flag = ' <-- BRACKET' if r[0] < 1.0 else ''
        print(f"  {r[0]:.3f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}{flag}")

asyncio.run(supp())
