import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    scored = []
    for m, (yb, nb) in zip(markets, books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        if m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        scored.append((yp + np, m.question[:60], yp, np, m.liquidity))
    scored.sort()
    return scored

scored = asyncio.run(scan())
floor = scored[0] if scored else None
print(f"min-ask scored markets: {len(scored)}")
if floor:
    print(f"TRUE FLOOR (min-ask sum): {floor[0]:.4f} | {floor[1]}")
under = [s for s in scored if s[0] <= 1.005]
print(f"min-ask <= 1.005: {len(under)}")
for t, q, yp, np, liq in under[:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
print(f"min-ask < 1.00 (real brackets): {sum(1 for s in scored if s[0] < 1.0)}")
