import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np, m.question[:50], yp, np, m.liquidity))
    rows.sort()
    print(f"priced markets (best-ask): {len(rows)}")
    if rows:
        print(f"floor sum: {rows[0][0]:.4f} | {rows[0][1]}")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"near-misses <=1.005 (best-ask): {len(nm)}")
    for total, q, yp, np, liq in nm[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    br = [r for r in rows if r[0] < 1.0]
    print(f"true brackets sum<1.00 (best-ask): {len(br)}")
    for total, q, yp, np, liq in br[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(supp())
