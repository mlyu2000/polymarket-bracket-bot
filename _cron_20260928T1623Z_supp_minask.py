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
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        priced += 1
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        s = ya + na
        rows.append((s, m.question[:50], ya, na, m.liquidity))
    rows.sort()
    print(f"priced markets: {priced}/{len(markets)}")
    print(f"floor (min sum via min-ask): {rows[0][0]:.4f}" if rows else "no rows")
    lm = [r for r in rows if r[0] <= 1.005]
    print(f"min-ask near-misses (<=1.005): {len(lm)}")
    for r in lm[:10]:
        print(f"  {r[0]:.3f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.0f} | {r[1]}")
    # machine-readable tail for persistence
    import json
    print("JSON:" + json.dumps({
        'priced': priced,
        'floor': rows[0][0] if rows else None,
        'near_misses': [[r[0], r[1], r[2], r[3], r[4]] for r in lm],
    }))

asyncio.run(supp())
