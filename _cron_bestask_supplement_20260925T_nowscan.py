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
        rows.append((y + n, y, n, m.question[:55], m.liquidity))
    rows.sort()
    print(f"min-ask scan: {len(markets)} markets in {dt:.1f}s")
    print(f"floor (best sum): {rows[0][0]:.4f}")
    lt1 = [r for r in rows if r[0] < 1.0]
    print(f"true brackets (min-ask sum < 1.00): {len(lt1)}")
    for s, y, n, q, liq in lt1:
        print(f"  BRACKET {s:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
    print("top 5 closest (min-ask):")
    for s, y, n, q, liq in rows[:5]:
        print(f"  {s:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")

asyncio.run(scan())
