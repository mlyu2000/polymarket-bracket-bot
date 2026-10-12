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

    priced = 0
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        priced += 1
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            rows.append((total, m.question[:50], yp, np, m.liquidity, 'BRACKET'))
        elif total <= 1.005:
            rows.append((total, m.question[:50], yp, np, m.liquidity, 'near'))
    rows.sort()
    print(f"PRICED MARKETS (best-ask): {priced}/{len(markets)}")
    if rows:
        print(f"BEST-ASK FLOOR: {rows[0][0]:.4f}")
    print(f"BRACKETS via detector: {sum(1 for r in rows if r[5]=='BRACKET')}")
    print(f"NEAR-MISS <=1.005 (best-ask): {len(rows)}")
    for total, q, yp, np, liq, tag in rows[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {tag} | {q}")

asyncio.run(scan())
