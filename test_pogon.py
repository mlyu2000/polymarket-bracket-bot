import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    target = "Will Pogon Szczecin win on 2026-08-23"
    for m in markets:
        if target in m.question:
            print("Found market")
            print(m.question)
            print(m.clob_token_ids)
            print(m.outcomes)
            yes_id = m.clob_token_ids[0]
            no_id = m.clob_token_ids[1]
            yes_book = await api.fetch_order_book(yes_id)
            no_book = await api.fetch_order_book(no_id)
            print("yes_book asks:", yes_book.asks[:3] if yes_book else None)
            print("no_book asks:", no_book.asks[:3] if no_book else None)
            # swap
            yes_book2 = await api.fetch_order_book(no_id)
            no_book2 = await api.fetch_order_book(yes_id)
            print("swapped yes asks:", yes_book2.asks[:3] if yes_book2 else None)
            print("swapped no asks:", no_book2.asks[:3] if no_book2 else None)
            break

asyncio.run(test())
