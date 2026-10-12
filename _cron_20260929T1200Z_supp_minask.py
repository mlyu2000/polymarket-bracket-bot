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
    brackets = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            s = yp + np
            if s < 1.0:
                brackets.append((s, m.question[:60], yp, np, m.liquidity))
            elif s <= 1.005:
                rows.append((s, m.question[:60], yp, np, m.liquidity))
    rows.sort(); brackets.sort()
    print(f"[min-ask supplement] {len(markets)} markets, {priced} with both books, in {dt:.1f}s")
    print(f"TRUE BRACKETS (min-ask sum<1.00): {len(brackets)}")
    for s, q, yp, np, liq in brackets[:10]:
        print(f"  🔴 {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"NEAR-MISS (min-ask sum<=1.005): {len(rows)}")
    for s, q, yp, np, liq in rows[:10]:
        print(f"  {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
