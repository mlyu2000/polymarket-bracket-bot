import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    count = 0
    near = []
    for m in markets:
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        count += 1
        yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
        no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
        yes_price = float(yes_ask["price"])
        no_price = float(no_ask["price"])
        total = yes_price + no_price
        if total <= 1.005:
            near.append((total, m.question[:60], yes_price, no_price))
    near.sort(key=lambda x: x[0])
    for t,q,yp,np in near[:20]:
        print(f"{t:.4f} Yes {yp:.3f} No {np:.3f} {q}")
    print(f"Checked {count}, near {len(near)}")

asyncio.run(test())
