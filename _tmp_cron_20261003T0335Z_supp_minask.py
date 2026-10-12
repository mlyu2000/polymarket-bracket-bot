"""Supplementary near-miss/floor check using BEST ASK (min price), per known
asks-DESC-sort issue: the verbatim cron script's asks[0] near-miss block is
biased toward the worst ask and always reports 0. This re-checks with min()."""
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
    best_floor = None
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        if m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        tot = yp + np_
        priced += 1
        if best_floor is None or tot < best_floor[0]:
            best_floor = (tot, m.question[:60], yp, np_, m.liquidity)
        if tot <= 1.005:
            rows.append((tot, m.question[:60], yp, np_, m.liquidity))

    rows.sort()
    print(f"priced markets (liq>0, both asks): {priced}")
    if best_floor:
        print(f"best floor seen: sum={best_floor[0]:.4f} | Yes@{best_floor[2]:.3f} No@{best_floor[3]:.3f} | liq={best_floor[4]:.0f} | {best_floor[1]}")
    print(f"near-misses (<=1.005, best-ask): {len(rows)}")
    for tot, q, yp, np_, liq in rows[:10]:
        print(f"  {tot:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")

asyncio.run(main())
