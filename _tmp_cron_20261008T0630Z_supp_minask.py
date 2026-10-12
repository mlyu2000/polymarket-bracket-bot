import asyncio, logging
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
    minsum = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            # asks are DESC-sorted; best ask = min price
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            t = yp + np
            if minsum is None or t < minsum[0]:
                minsum = (t, m.question[:60])
            if t < 1.005:
                rows.append((t, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    print(f"priced markets (min-ask basis): {priced}")
    if minsum:
        print(f"GLOBAL MIN SUM: {minsum[0]:.4f} | {minsum[1]}")
    print(f"markets with min-ask sum <= 1.005: {len(rows)}")
    for t, q, yp, np, liq in rows[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    lt1 = [r for r in rows if r[0] < 1.0]
    print(f"sum < 1.000 (true brackets on best-ask basis): {len(lt1)}")
    for t, q, yp, np, liq in lt1[:10]:
        print(f"  RED {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
