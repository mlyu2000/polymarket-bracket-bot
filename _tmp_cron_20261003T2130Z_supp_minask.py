"""Supplementary: correct best-ask (min) totals across all active markets,
since the cron script's near-miss block uses asks[0] (DESC-sorted = worst ask).
Also reports why detector found no brackets: min-ask sum < 1.00 vs net-edge gate."""
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not m.active or m.closed:
            continue
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        if m.liquidity <= 0:
            continue
        yp = min(float(a["price"]) for a in yb.asks)
        np_ = min(float(a["price"]) for a in nb.asks)
        if yp <= 0 or np_ <= 0 or yp >= 1 or np_ >= 1:
            continue
        priced += 1
        total = yp + np_
        rows.append((total, m.question[:60], yp, np_, m.liquidity))

    rows.sort()
    print(f"active-priced markets: {priced}")
    if rows:
        print(f"floor sum: {rows[0][0]:.4f}")
    n_lt1 = sum(1 for r in rows if r[0] < 1.0)
    n_le1005 = sum(1 for r in rows if r[0] <= 1.005)
    print(f"sum<1.00: {n_lt1} | sum<=1.005: {n_le1005}")
    print("top8 lowest sums (best-ask min):")
    for total, q, yp, np_, liq in rows[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(main())
