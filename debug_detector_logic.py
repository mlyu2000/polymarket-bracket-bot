import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    count = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
        no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
        yes_price = float(yes_ask["price"])
        no_price = float(no_ask["price"])
        if yes_price >= 1.0 or no_price >= 1.0:
            continue
        if yes_price <= 0 or no_price <= 0:
            continue
        yes_volume = int(float(yes_ask["size"]))
        no_volume = int(float(no_ask["size"]))
        max_shares = min(yes_volume, no_volume)
        if max_shares <= 0:
            continue
        total_cost = yes_price + no_price
        gross_edge = 1.00 - total_cost
        net_edge = gross_edge - Config.FEE_BUFFER - Config.SLIPPAGE_BUFFER
        if net_edge >= Config.MIN_PROFIT_MARGIN:
            print(f"Potential: {m.question[:60]} yes={yes_price} no={no_price} sum={total_cost} edge={net_edge} shares={max_shares} liq={m.liquidity}")
            count += 1
    print(f"Count: {count}")

asyncio.run(test())
