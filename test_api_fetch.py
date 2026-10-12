import asyncio
import httpx

async def test():
    # Let's inspect what PolymarketAPI does
    import sys
    sys.path.insert(0, '/home/ml/projects/polymarket-bracket-bot')
    from config import Config
    Config.validate()
    from polymarket_api import PolymarketAPI
    api = PolymarketAPI()
    # test fetch_order_book
    # Use a token that we know works from previous run
    token_id = '64469905005594457751898719080337446869920751709911938125552180158868954986760'
    book = await api.fetch_order_book(token_id)
    print(book)
    if book:
        print("asks:", book.asks[:2])
        print("bids:", book.bids[:2])

asyncio.run(test())
