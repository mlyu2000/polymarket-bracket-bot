"""Supplementary pass: near-misses/brackets computed from BEST asks (min price),
since CLOB /book asks are DESC-sorted and asks[0] is the worst quote.
Also lists true minimum sum across all scanned markets."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)

    rows = []
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np, m.question[:60], yp, np, m.liquidity, m.active, m.closed))

    rows.sort()
    print(f"markets={len(markets)} priced={len(rows)}")
    lt1 = [r for r in rows if r[0] < 1.0]
    print(f"TRUE_BRACKETS(sum<1.00 via best asks): {len(lt1)}")
    for t, q, yp, np, liq, act, cl in lt1:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} active={act} closed={cl} | {q}")
    print("TOP10_BEST_SUMS:")
    for t, q, yp, np, liq, act, cl in rows[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")

asyncio.run(scan())
