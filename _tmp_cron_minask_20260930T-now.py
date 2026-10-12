"""Supplementary pass: near-misses/brackets from BEST asks (min price),
since CLOB /book asks are DESC-sorted and asks[0] is the worst quote.
Also lists true minimum sum across all scanned markets."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    rows = []
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity, m.active, m.closed))

    rows.sort()
    print(f"markets={len(markets)} priced={len(rows)} scan={dt:.1f}s")
    lt1 = [r for r in rows if r[0] < 1.0]
    print(f"TRUE_BRACKETS(sum<1.00 via best asks): {len(lt1)}")
    for r in lt1[:10]:
        act = 'ACTIVE' if (r[5] and not r[6]) else 'INACTIVE/CLOSED'
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.0f} | {act} | {r[1]}")
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"NEAR_MISSES(1.000-1.005): {len(nm)}")
    for r in nm[:10]:
        act = 'ACTIVE' if (r[5] and not r[6]) else 'INACTIVE/CLOSED'
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.0f} | {act} | {r[1]}")
    if rows:
        r = rows[0]
        print(f"GLOBAL_MIN_SUM: {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | {r[1]}")

asyncio.run(scan())
