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

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            continue  # already reported as bracket
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # CORRECTED: best ask = min price (asks are DESC-sorted)
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            priced += 1
            rows.append((total, m.question[:60], yes_price, no_price, m.liquidity))
    rows.sort()
    return len(markets), priced, rows

markets_n, priced_n, rows = asyncio.run(scan())
print(f"Markets fetched: {markets_n} | priced (both books have asks): {priced_n}")
print(f"MIN best-ask sum across all priced markets: {rows[0][0]:.4f}")
print("Top-10 closest to bracket (best-ask Yes+No sums):")
for total, q, yp, np, liq in rows[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:,.0f} | {q}")
print(f"Count sum<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
print(f"Count sum<=1.01:  {sum(1 for r in rows if r[0] <= 1.01)}")
