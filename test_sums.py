import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=20)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    sums = []
    for m, (yes_book, no_book) in zip(markets, books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
            no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
            yes_price = float(yes_ask["price"])
            no_price = float(no_ask["price"])
            total = yes_price + no_price
            sums.append((total, m.question[:60], yes_price, no_price, m.liquidity))
    sums.sort()
    print(f"Checked {len(sums)} markets")
    for total, q, yp, np, liq in sums[:20]:
        print(f"{total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(test())
