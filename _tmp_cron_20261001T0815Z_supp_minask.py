import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    totals = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        # CLOB /book asks are DESC-sorted -> best (cheapest) ask = min()
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        totals.append((yp + np, m.question[:50], yp, np, m.liquidity))

    totals.sort()
    print(f"markets={len(markets)} priced={len(totals)} time={dt:.1f}s")
    lt1 = [t for t in totals if t[0] < 1.0]
    print(f"TRUE brackets (best-ask sum < 1.000): {len(lt1)}")
    for t, q, yp, np, liq in lt1[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    lt1005 = [t for t in totals if t[0] <= 1.005]
    print(f"best-ask near-misses (sum <= 1.005): {len(lt1005)}")
    for t, q, yp, np, liq in lt1005[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print("Floor (10 lowest sums):")
    for t, q, yp, np, liq in totals[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
