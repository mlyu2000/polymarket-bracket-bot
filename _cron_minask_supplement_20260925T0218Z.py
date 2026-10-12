import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    totals = []
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        totals.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    totals.sort()
    return totals

t0 = time.time()
totals = asyncio.run(scan())
print(f"min-ask totals computed for {len(totals)} priced markets in {time.time()-t0:.1f}s")
print("FLOOR (8 best):")
for total, q, yp, np_, liq in totals[:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
brackets = [t for t in totals if t[0] < 1.0]
near = [t for t in totals if 1.0 <= t[0] <= 1.005]
print(f"TRUE BRACKETS (min-ask sum<1.0): {len(brackets)}")
for total, q, yp, np_, liq in brackets:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"NEAR-MISS 1.000-1.005: {len(near)}")
for total, q, yp, np_, liq in near[:5]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
