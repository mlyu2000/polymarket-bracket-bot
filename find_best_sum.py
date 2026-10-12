import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def find_min_sum():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    # filter markets with liquidity >=100
    filtered = [m for m in markets if m.liquidity >= 100]
    print('filtered', len(filtered))
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in filtered]
    books = await api.fetch_order_books_batch(token_pairs)
    best = None
    for m, (yes,no) in zip(filtered, books):
        if not yes or not no or not yes.asks or not no.asks:
            continue
        yes_ask = min(yes.asks, key=lambda a: float(a['price']))
        no_ask = min(no.asks, key=lambda a: float(a['price']))
        total = float(yes_ask['price'])+float(no_ask['price'])
        if best is None or total < best[0]:
            best = (total, m.question[:80], yes_ask, no_ask, m.liquidity)
    print('best', best)

asyncio.run(find_min_sum())
