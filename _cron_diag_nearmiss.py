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

    # Use min() (best ask) consistently — matches detector logic
    near_misses = []
    exact_brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            exact_brackets.append(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_price = float(min(yes_book.asks, key=lambda a: float(a["price"]))["price"])
                no_price = float(min(no_book.asks, key=lambda a: float(a["price"]))["price"])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:60], yes_price, no_price, m.liquidity))
    near_misses.sort()
    return len(markets), len(exact_brackets), near_misses

n, b, nm = asyncio.run(scan())
print(f"Markets: {n}")
print(f"BRACKETS (net_edge>=0.01): {b}")
print(f"NEAR-MISSES via min() (≤1.005): {len(nm)}")
for total, q, yp, np, liq in nm[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
