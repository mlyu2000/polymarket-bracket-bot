import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets(limit=500)
    print(f"Fetched {len(markets)} in {time.time()-t0:.1f}s")
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs, batch_size=20)
    brackets = []
    near = []
    for m, (yes_b, no_b) in zip(markets, books):
        if not yes_b or not no_b: continue
        if not yes_b.asks or not no_b.asks: continue
        if m.liquidity < Config.MIN_LIQUIDITY_USDC: continue
        yes_price = float(min(yes_b.asks, key=lambda a: float(a['price']))['price'])
        no_price = float(min(no_b.asks, key=lambda a: float(a['price']))['price'])
        total = yes_price + no_price
        if total < 1.0:
            brackets.append((total, m.question[:60], yes_price, no_price, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:60], yes_price, no_price))
    print(f"Brackets sum<1.0: {len(brackets)}")
    for b in sorted(brackets)[:20]:
        print(b)
    print(f"Near <=1.005: {len(near)}")
    for n in sorted(near)[:10]:
        print(n)

asyncio.run(test())
