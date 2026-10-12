import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            priced += 1
            rows.append((yp + np, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    return len(markets), priced, rows

markets_n, priced, rows = asyncio.run(scan())
print(f"[min-ask pass] markets={markets_n} priced={priced}")
if rows:
    floor = rows[0]
    print(f"TRUE FLOOR (min Yes ask + min No ask): {floor[0]:.4f} | Yes@{floor[2]:.3f} No@{floor[3]:.3f} | liq={floor[4]} | {floor[1]}")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"Near-misses (<=1.005): {len(nm)}")
    for total, q, yp, np, liq in nm[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    below1 = [r for r in rows if r[0] < 1.0]
    print(f"Sums < 1.000: {len(below1)}")
    for total, q, yp, np, liq in below1[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
