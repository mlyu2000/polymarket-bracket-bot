import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    totals = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            totals.append((yp + np_, m.question[:55], yp, np_, m.liquidity))

    totals.sort()
    print(f"priced markets: {len(totals)}")
    print("best min-ask sums:")
    for t, q, yp, np_, liq in totals[:8]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:,.0f} | {q}")
    print(f"sum<1.00: {sum(1 for x in totals if x[0] < 1.0)}")
    print(f"sum<=1.005: {sum(1 for x in totals if x[0] <= 1.005)}")
    print(f"sum<=1.01: {sum(1 for x in totals if x[0] <= 1.01)}")

asyncio.run(scan())
