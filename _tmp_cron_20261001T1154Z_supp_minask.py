import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    results = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        if m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        priced += 1
        results.append((total, m.question[:60], yp, np, m.liquidity))

    results.sort()
    print(f"priced markets (liq>0): {priced}")
    print("true floor (min sum across all):", f"{results[0][0]:.4f}" if results else "none")
    print("best 10 by min-ask sum:")
    for total, q, yp, np, liq in results[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
    below = [r for r in results if r[0] < 1.0]
    near = [r for r in results if 1.0 <= r[0] <= 1.005]
    print(f"sums < 1.00: {len(below)} ; near-misses [1.00,1.005]: {len(near)}")
    for total, q, yp, np, liq in below[:10]:
        print(f"  SUB-1 {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")

asyncio.run(supp())
