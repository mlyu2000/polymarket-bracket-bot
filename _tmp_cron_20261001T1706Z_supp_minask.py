import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    priced = 0
    minima = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            minima.append((yp + np, m.question[:50], yp, np, m.liquidity))
    minima.sort()
    print(f"Priced markets (min-ask basis): {priced}/{len(markets)}")
    print(f"sum<1.000: {sum(1 for t,*_ in minima if t < 1.0)}")
    print(f"sum<=1.005: {sum(1 for t,*_ in minima if t <= 1.005)}")
    print(f"sum<=1.01: {sum(1 for t,*_ in minima if t <= 1.01)}")
    print("Top 5 closest (min best asks):")
    for total, q, yp, np, liq in minima[:5]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(supp())
