import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def floor():
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
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    print(f"[floor] {len(markets)} markets, {priced} with two-sided asks, {dt:.1f}s")
    if rows:
        print(f"[floor] best sum = {rows[0][0]:.4f}  worst-of-top = {rows[-1][0]:.4f}")
    print(f"[floor] TOP 10 by min-ask sum:")
    for s, q, yp, np, liq in rows[:10]:
        flag = " <<< BRACKET" if s < 1.0 else ""
        print(f"  {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}{flag}")

asyncio.run(floor())
