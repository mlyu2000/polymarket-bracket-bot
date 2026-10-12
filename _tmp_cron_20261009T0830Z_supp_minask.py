import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    print(f"markets priced: {len(rows)}")
    print("best 8 by min-ask sum:")
    for total, q, yp, np, liq in rows[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    lt1 = [r for r in rows if r[0] < 1.0]
    print(f"true floor check: {len(lt1)} markets with min-ask sum < 1.0")
    import json
    with open('_tmp_cron_20261009T0830Z_supp_data.json', 'w') as f:
        json.dump({'rows': rows[:20], 'lt1': lt1}, f)

asyncio.run(supp())
