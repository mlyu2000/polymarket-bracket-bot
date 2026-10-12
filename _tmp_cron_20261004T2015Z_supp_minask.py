"""Corrected near-miss/floor supplement: best ask = MIN of asks (CLOB sends DESC-sorted asks)."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        if yp <= 0 or np <= 0 or yp >= 1 or np >= 1:
            continue
        priced += 1
        rows.append((yp + np, m.question[:60], yp, np, m.liquidity))

    rows.sort()
    print(f"priced markets: {priced}")
    if rows:
        print(f"floor (min sum): {rows[0][0]:.4f}")
        print("top-10 closest to bracket:")
        for s, q, yp, np, liq in rows[:10]:
            flag = " <1.00!" if s < 1.0 else ""
            print(f"  {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}{flag}")
    return rows

asyncio.run(scan())
