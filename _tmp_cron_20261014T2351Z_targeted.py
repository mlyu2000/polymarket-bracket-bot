"""Targeted: where did BTC 'above $72,000 Oct 16' and Jablonec -2.5 land?
They were in the floor tier at 23:37Z but are absent from the 23:52Z top-25."""
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)


async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    targets = [m for m in markets if ('72,000' in m.question or 'Bitcoin above' in m.question
               or 'Jablonec' in m.question)]
    if not targets:
        print('NO MATCHING MARKETS FOUND')
        return
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in targets]
    books = await api.fetch_order_books_batch(token_pairs)

    def best(book):
        if not book or not book.asks:
            return None
        return min(float(a['price']) for a in book.asks)

    for m, (yb, nb) in zip(targets, books):
        y = best(yb)
        n = best(nb)
        tot = (y + n) if (y is not None and n is not None) else None
        print(f"{m.question[:70]!r} | Ymin={y} Nmin={n} | sum={tot} | liq={m.liquidity}")


asyncio.run(main())
