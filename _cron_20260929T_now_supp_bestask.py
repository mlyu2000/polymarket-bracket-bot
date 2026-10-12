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
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        y = min(float(a['price']) for a in yes_book.asks)
        n = min(float(a['price']) for a in no_book.asks)
        total = y + n
        opp = detector.detect(m, yes_book, no_book)
        if total < 1.0:
            brackets.append((total, y, n, m.liquidity, m.question[:70], opp.net_edge if opp else None))
        if total <= 1.01:
            rows.append((total, y, n, m.liquidity, m.question[:70]))
    rows.sort()
    brackets.sort()
    print(f"markets={len(markets)} best-ask-sum<1.00 count={len(brackets)}")
    for t, y, n, liq, q, e in brackets:
        print(f"BRACKET best-sum={t:.4f} Yes@{y:.3f} No@{n:.3f} liq={liq} detedge={e} | {q}")
    print("--- top 8 best-ask near-misses (<=1.01) ---")
    for t, y, n, liq, q in rows[:8]:
        print(f"  {t:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")

asyncio.run(scan())
