import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    if not book or not book.asks:
        return None
    return min(float(a['price']) for a in book.asks)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        yp, np = best_ask(yb), best_ask(nb)
        if yp is None or np is None:
            continue
        priced += 1
        rows.append((yp + np, m.question[:70], yp, np, m.liquidity))
    rows.sort()
    print(f"priced markets: {priced}")
    print("closest 8 by best-ask sum:")
    for total, q, yp, np, liq in rows[:8]:
        flag = "BRACKET" if total < 1.0 else ("near" if total <= 1.005 else "")
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q} {flag}")

asyncio.run(supp())
