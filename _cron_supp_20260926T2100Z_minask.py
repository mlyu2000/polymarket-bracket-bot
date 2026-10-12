# Supplement: true best-ask (min) floor. asks[0] on CLOB is the WORST ask (DESC sort).
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
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            s = min(float(a['price']) for a in yb.asks) + min(float(a['price']) for a in nb.asks)
            rows.append((s, m.question[:50], m.liquidity))
    rows.sort()
    print(f"[min-ask supplement] {priced}/{len(markets)} priced markets in {dt:.1f}s")
    for s, q, liq in rows[:5]:
        print(f"  sum={s:.4f} | liq={liq} | {q}")

asyncio.run(scan())
