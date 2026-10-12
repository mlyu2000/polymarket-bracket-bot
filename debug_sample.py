import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    ms = await api.fetch_active_markets(limit=5)
    print([m.question[:60] for m in ms])
    for m in ms:
        print(m.liquidity, m.clob_token_ids)
    b = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1]) for m in ms])
    print('books', len(b))
    import json
    out = []
    for i in range(len(b)):
        y, n = b[i]
        out.append({
            'asks': y.asks[:2] if y else None,
            'no_asks': n.asks[:2] if n else None
        })
    print(json.dumps(out, indent=2))

asyncio.run(f())
