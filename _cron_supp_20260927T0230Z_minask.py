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
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        y = min(float(a['price']) for a in yb.asks)
        n = min(float(a['price']) for a in nb.asks)
        rows.append((y + n, m.question[:60], y, n, m.liquidity))
    rows.sort()
    print(f"min-ask method: {len(rows)} priced markets in {dt:.1f}s")
    print("TRUE BRACKETS (sum < 1.000):")
    br = [r for r in rows if r[0] < 1.0]
    if not br:
        print("  none")
    for t, q, y, n, liq in br:
        print(f"  {t:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
    print("TOP-8 CLOSEST (sum >= 1.000):")
    for t, q, y, n, liq in [r for r in rows if r[0] >= 1.0][:8]:
        print(f"  {t:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")

asyncio.run(scan())
