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
    for m, (yb, nb) in zip(markets, books):
        if 'Bournemouth' in m.question or 'Bitcoin' in m.question:
            def stat(b):
                if not b or not b.asks:
                    return 'NO ASKS'
                return f"min={min(float(a['price']) for a in b.asks):.3f} n={len(b.asks)}"
            print(f"{m.question[:60]} | YES[{stat(yb)}] NO[{stat(nb)}] | liq={m.liquidity} | closed={getattr(m,'closed','?')} active={getattr(m,'active','?')}")
asyncio.run(main())
