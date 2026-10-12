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
            brackets.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:70]))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            npr = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + npr, m.question[:70], yp, npr, m.liquidity))
    rows.sort()
    return rows, brackets

rows, brackets = asyncio.run(scan())
print(f"BRACKETS via detector: {len(brackets)}")
for b in sorted(brackets)[:10]:
    print(f"  {b[0]:.3f} edge={b[1]:.4f} shares={b[2]} | {b[3]}")
print("TOP 12 by BEST-ASK (min) total Yes+No:")
for total, q, yp, npr, liq in rows[:12]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")
