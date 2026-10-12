import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    both = yes_none = no_none = empty_asks = 0
    for (yb, nb) in all_books:
        if yb is None or nb is None:
            if yb is None: yes_none += 1
            if nb is None: no_none += 1
            both += 0
        elif not yb.asks or not nb.asks:
            empty_asks += 1
        else:
            both += 1
    return len(markets), both, yes_none, no_none, empty_asks

n, both, yn, nn, ea = asyncio.run(scan())
print(f"markets={n} priced(yb+nb both w/asks)={both} yes_book_none={yn} no_book_none={nn} empty_asks={ea}")
