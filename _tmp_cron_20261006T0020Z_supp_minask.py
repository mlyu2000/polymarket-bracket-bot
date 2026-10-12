import asyncio, logging, time
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

    rows = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60], m.liquidity))
        if yes_book and no_book and getattr(yes_book, 'asks', None) and getattr(no_book, 'asks', None):
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np, m.question[:55], yp, np, m.liquidity))

    rows.sort()
    brackets.sort()
    print(f"markets={len(markets)} priced={len(rows)}")
    print(f"BRACKETS via detector (min-ask): {len(brackets)}")
    for b in brackets[:10]:
        print(f"  B {b[0]:.4f} edge={b[1]:.4f} shares={b[2]} liq={b[4]} | {b[3]}")
    print("TOP 10 best min-ask sums:")
    for t, q, yp, np, liq in rows[:10]:
        print(f"  {t:.4f} | Y@{yp:.3f} N@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
