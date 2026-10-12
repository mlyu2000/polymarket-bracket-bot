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
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        rows.append((yp + np, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    print(f"min-ask supplement: {len(markets)} markets in {dt:.1f}s")
    print(f"priced: {len(rows)}")
    for total, q, yp, np, liq in rows[:10]:
        flag = " <1.00 BRACKET" if total < 1.0 else (" <=1.005" if total <= 1.005 else "")
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq}{flag} | {q}")

asyncio.run(scan())
