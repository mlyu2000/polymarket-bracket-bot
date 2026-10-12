import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            rows.append((yes_price + no_price, m.question[:60], yes_price, no_price, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(supp())
print(f"priced markets: {len(rows)}")
print("floor (min sum): %.4f" % rows[0][0] if rows else "no data")
print("--- top 10 closest to <=1.005 (best asks) ---")
for total, q, yp, np, liq in rows[:10]:
    flag = "NEAR<=1.005" if total <= 1.005 else ""
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q} {flag}")
