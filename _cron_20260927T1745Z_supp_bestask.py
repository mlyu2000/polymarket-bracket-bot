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
    el = time.time() - t0
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yy = min(float(a['price']) for a in yb.asks)
        yn = min(float(a['price']) for a in nb.asks)
        rows.append((yy + yn, m.question[:55], yy, yn, m.liquidity))
    rows.sort()
    print(f"True best-ask sums ({len(rows)} priced markets) in {el:.1f}s:")
    print("FLOOR (10 lowest):")
    for s, q, a, b, l in rows[:10]:
        print(f"  {s:.4f} | Y@{a:.3f} N@{b:.3f} | liq={l} | {q}")
    brk = [r for r in rows if r[0] < 1.0]
    nm5 = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"count sum<1.000: {len(brk)} | count 1.000-1.005: {len(nm5)}")
    for s, q, a, b, l in brk + nm5:
        print(f"  {'BRACKET' if s < 1.0 else 'NEAR   '} {s:.4f} | Y@{a:.3f} N@{b:.3f} | liq={l} | {q}")

asyncio.run(scan())
