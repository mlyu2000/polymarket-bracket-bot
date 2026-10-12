"""Supplement: true best-ask (min) sums, since asks are DESC-sorted."""
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
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    rows.sort()
    print(f"priced markets (min-ask): {len(rows)}")
    lt1 = [r for r in rows if r[0] < 1.0]
    print(f"sums < 1.000: {len(lt1)}")
    for t, q, yp, np_, liq in lt1[:10]:
        print(f"  *** {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
    print("floor (lowest 8 sums):")
    for t, q, yp, np_, liq in rows[:8]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"true near-misses (1.000-1.005]: {len(nm)}")
    for t, q, yp, np_, liq in nm[:5]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")

asyncio.run(main())
