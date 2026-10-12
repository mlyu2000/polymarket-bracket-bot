import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    targets = []
    for m in markets:
        q = m.question.lower()
        if ('levante' in q and 'ou 4.5' in q) or ('seville' in q and 'ou 4.5' in q):
            targets.append(('Levante/Sevilla O/U 4.5', m))
        if 'galatasaray' in q and '(-2.5)' in q:
            targets.append(('Galatasaray -2.5', m))

    for label, m in targets:
        results = await api.fetch_order_books_batch(
            [(m.clob_token_ids[0], m.clob_token_ids[1])]
        )
        yb, nb = results[0]
        print(f"--- {label}")
        print(f"    q={m.question[:70]}")
        print(f"    liquidity=${m.liquidity:,.0f} volume=${m.volume:,.0f} active={m.active} closed={m.closed}")
        for side, bk in (('YES', yb), ('NO', nb)):
            if not bk:
                print(f"    {side}: NO BOOK")
                continue
            asks = bk.asks or []
            bids = bk.bids or []
            ymin = min((float(a['price']) for a in asks), default=None)
            print(f"    {side}: asks={len(asks)} bids={len(bids)} min_ask={ymin} asks[0]={asks[0]['price'] if asks else None}")

asyncio.run(main())
