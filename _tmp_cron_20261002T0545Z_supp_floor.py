import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    sums = []
    brackets = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets += 1
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            sums.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    sums.sort()
    print(f"priced markets: {len(sums)} | detector brackets: {brackets}")
    print("global floor (best-ask sums, 5 lowest):")
    for s, q, yp, np_, liq in sums[:5]:
        print(f"  {s:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
