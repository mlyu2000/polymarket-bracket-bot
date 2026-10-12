import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    ms = [m for m in markets if 'Microsoft' in m.question and 'largest company' in m.question.lower()]
    print(f"Microsoft-largest-company markets in active set: {len(ms)}")
    for m in ms:
        print(f"  q={m.question[:70]} | liq={m.liquidity} | tokens={len(m.clob_token_ids)}")
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes_book, no_book = books[0]
        for side, b in (('yes', yes_book), ('no', no_book)):
            if b and b.asks:
                mn = min(float(a['price']) for a in b.asks)
                print(f"    {side}: asks={len(b.asks)} min={mn:.3f} ask0={float(b.asks[0]['price']):.3f}")
            else:
                print(f"    {side}: NO ASKS (book empty/None)")
        if yes_book and no_book and yes_book.asks and no_book.asks:
            s = min(float(a['price']) for a in yes_book.asks) + min(float(a['price']) for a in no_book.asks)
            print(f"    min-ask sum = {s:.4f}")

asyncio.run(check())
