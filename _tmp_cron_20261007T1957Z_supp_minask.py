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

    true_brackets = []
    near_misses = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            continue  # already reported by verbatim scan
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            if total < 1.0:
                true_brackets.append((total, m.question[:50], yes_price, no_price, m.liquidity))
            elif total <= 1.005:
                near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    true_brackets.sort()
    near_misses.sort()
    print(f"Markets with priced books (min-ask basis): {priced}")
    print(f"TRUE BRACKETS (min-ask sum < 1.00, below detector floor): {len(true_brackets)}")
    for total, q, yp, np, liq in true_brackets[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"NEAR-MISSES (min-ask sum <= 1.005): {len(near_misses)}")
    for total, q, yp, np, liq in near_misses[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
