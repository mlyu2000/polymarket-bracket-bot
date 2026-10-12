import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    count = 0
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
        gross_edge = 1.0 - total
        fee_buffer = Config.FEE_BUFFER
        slippage_buffer = Config.SLIPPAGE_BUFFER
        net_edge = gross_edge - fee_buffer - slippage_buffer
        if net_edge >= Config.MIN_PROFIT_MARGIN:
            print(f"Bracket: {total:.4f} net_edge {net_edge:.4f} {m.question[:60]}")
    print(f"Checked {count} markets")

asyncio.run(test())
