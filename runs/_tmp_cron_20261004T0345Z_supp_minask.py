import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    priced = 0
    min_near = []
    all_sums = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            total = ya + na
            all_sums.append((total, m.question[:60], ya, na, m.liquidity))

    all_sums.sort()
    min_near = [s for s in all_sums if s[0] <= 1.005]
    le1010 = [s for s in all_sums if s[0] <= 1.010]
    print(f"markets={len(markets)} both-sides-priced={priced} detector-brackets={len(brackets)}")
    print(f"FLOOR (min-ask): {all_sums[0][0]:.3f} | {all_sums[0][1]} | yesAsk={all_sums[0][2]:.3f} noAsk={all_sums[0][3]:.3f} liq={all_sums[0][4]}")
    print(f"min-ask near-misses <=1.005: {len(min_near)}")
    for total, q, yp, np, liq in min_near:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"count<=1.010: {len(le1010)}")

asyncio.run(scan())
