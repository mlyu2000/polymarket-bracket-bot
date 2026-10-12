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
    print(f"best-ask floor scan: {priced}/{len(markets)} priced markets in {dt:.1f}s")
    print("top 8 lowest YES+NO best-ask sums:")
    for total, q, yp, np, liq in rows[:8]:
        flag = "BRACKET" if total < 1.0 else "near" if total <= 1.005 else ""
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q} {flag}")

asyncio.run(scan())
