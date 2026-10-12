import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def run():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            rows.append((ya + na, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    print(f"priced markets: {len(rows)}")
    print(f"true floor (min-ask sum): {rows[0][0]:.3f}")
    lt1 = [r for r in rows if r[0] < 1.0]
    le1005 = [r for r in rows if r[0] <= 1.005]
    print(f"sum<1.000: {len(lt1)} | sum<=1.005: {len(le1005)}")
    for t, q, ya, na, liq in rows[:8]:
        print(f"  {t:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(run())
