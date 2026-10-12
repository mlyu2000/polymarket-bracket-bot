import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    best = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        priced += 1
        best.append((total, m.question[:60], yp, np, m.liquidity))

    best.sort()
    print(f"priced markets (best-ask): {priced}")
    print("top 8 by best-ask sum:")
    for total, q, yp, np, liq in best[:8]:
        flag = "<<< BRACKET" if total < 1.0 else ""
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q} {flag}")
    brackets = [b for b in best if b[0] < 1.0]
    print(f"best-ask brackets (sum<1.0): {len(brackets)}")

asyncio.run(scan())
