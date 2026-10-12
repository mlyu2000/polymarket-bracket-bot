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
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        priced += 1
        rows.append((total, m.question[:55], yp, np, m.liquidity))

    rows.sort()
    print(f"⏱️ {len(markets)} markets fetched in {dt:.1f}s | {priced} with two-sided asks")
    brackets = [r for r in rows if r[0] < 1.0]
    near = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"🔴 TRUE BRACKETS (min-ask sum < 1.000): {len(brackets)}")
    for total, q, yp, np, liq in brackets[:10]:
        print(f"  sum={total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"📊 NEAR-MISSES (1.000–1.005): {len(near)}")
    for total, q, yp, np, liq in near[:10]:
        print(f"  sum={total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print("📉 BOTTOM 10 BY SUM:")
    for total, q, yp, np, liq in rows[:10]:
        print(f"  sum={total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
