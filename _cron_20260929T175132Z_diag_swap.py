import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    empties = []
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and not nb.asks:
            empties.append((m, yb, nb))
    print(f"markets with yes-asks but empty no-asks: {len(empties)}")
    for m, yb, nb in empties[:3]:
        print('---', m.question[:70])
        print('  no_book bids:', len(nb.bids) if nb.bids else 0, '| asks:', len(nb.asks) if nb.asks else 0)
        # try swapping: maybe clob_token_ids order != yes/no order
        print('  token0:', m.clob_token_ids[0][:16], '... token1:', m.clob_token_ids[1][:16], '...')
        print('  outcomes:', getattr(m, "outcomes", None))
        ob = await api.fetch_order_book(m.clob_token_ids[1])
        print('  re-fetch token1 alone -> asks:', len(ob.asks) if ob and ob.asks else (0 if ob is not None else 'None'), '| bids:', len(ob.bids) if ob and ob.bids else 0)

asyncio.run(main())
