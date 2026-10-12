"""Corrected near-miss / floor check using min(asks) per side (known CLOB sort quirk)."""
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)

    priced = 0
    near = []
    floor = None
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        total = yp + np_
        priced += 1
        if floor is None or total < floor[0]:
            floor = (total, m.question[:60])
        if total <= 1.005:
            near.append((total, m.question[:60], yp, np_, m.liquidity))
    near.sort()
    print(f"priced markets: {priced}")
    print(f"floor: {floor[0]:.4f} | {floor[1]}" if floor else "floor: n/a")
    print(f"near-misses <=1.005 (min-ask): {len(near)}")
    for t, q, yp, np_, liq in near[:10]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(main())
