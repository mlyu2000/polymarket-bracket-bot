import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
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
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np, m.question[:55], yp, np, m.liquidity))
    rows.sort()
    print(f"markets={len(markets)} priced={priced}")
    lt1 = [r for r in rows if r[0] < 1.0]
    print(f"min_ask_sum_below_1.00 = {len(lt1)}")
    print("top8 true floors:")
    for t, q, yp, np, liq in rows[:8]:
        print(f"  {t:.4f} | Y@{yp:.3f} N@{np:.3f} | liq={liq:.0f} | {q}")

asyncio.run(scan())
