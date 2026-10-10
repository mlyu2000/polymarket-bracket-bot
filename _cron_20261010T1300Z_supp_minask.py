import asyncio, json, time
from config import Config
from polymarket_api import PolymarketAPI

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            npp = min(float(a['price']) for a in nb.asks)
            total = yp + npp
            if total < 1.02:
                rows.append((total, m.question[:60], yp, npp, m.liquidity))
            priced += 1
    rows.sort()
    print(f"priced markets (both books have asks): {priced}/{len(markets)}")
    print(f"true floor (min-ask sum): {rows[0][0]:.3f}" if rows else "no priced rows")
    print("--- closest 8 (min-ask sums) ---")
    for total, q, yp, npp, liq in rows[:8]:
        print(f"{total:.3f} | Yes@{yp:.3f} No@{npp:.3f} | liq {liq:.1f} | {q}")

asyncio.run(main())
