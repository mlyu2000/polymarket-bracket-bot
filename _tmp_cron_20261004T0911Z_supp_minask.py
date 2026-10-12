# Supplement: true best-ask (min) floor check — CLOB asks are DESC-sorted, asks[0] is worst
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
            ym = min(float(a['price']) for a in yb.asks)
            nm = min(float(a['price']) for a in nb.asks)
            rows.append((ym + nm, m.question[:60], ym, nm, m.liquidity))
    rows.sort()
    print(f"minask scan: {len(markets)} markets, {priced} priced pairs in {dt:.1f}s")
    if rows:
        print(f"TRUE FLOOR (min asks): {rows[0][0]:.4f} | Yes@{rows[0][2]:.3f} No@{rows[0][3]:.3f} | {rows[0][1]}")
    br = [r for r in rows if r[0] < 1.0]
    nm5 = [r for r in rows if r[0] <= 1.005]
    print(f"brackets(min sum<1.00): {len(br)} | near-misses(min <=1.005): {len(nm5)}")
    show = nm5 if nm5 else rows
    for s, q, ym, nm, liq in show[:8]:
        print(f"  {s:.4f} | Yes@{ym:.3f} No@{nm:.3f} | liq={liq} | {q}")

asyncio.run(scan())
