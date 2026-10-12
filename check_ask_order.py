import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    yes_id, no_id = m.clob_token_ids
    yes_book = await api.fetch_order_book(yes_id)
    print("asks count", len(yes_book.asks))
    print("first 10 prices:", [a['price'] for a in yes_book.asks[:10]])
    # check if sorted
    prices = [float(a['price']) for a in yes_book.asks]
    is_sorted = all(prices[i] >= prices[i+1] for i in range(len(prices)-1))
    print("descending?", is_sorted)
    # find min
    print("min price", min(prices))

asyncio.run(main())
