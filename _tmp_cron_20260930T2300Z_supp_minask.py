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
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            rows.append((opp.total_cost, 'BRACKET', opp.yes_price, opp.no_price, m.question[:50], m.liquidity, opp.max_shares, opp.net_edge))
        elif yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            rows.append((ya + na, 'min-ask', ya, na, m.question[:50], m.liquidity, 0, 0.0))

    rows.sort()
    print(f"total markets: {len(rows)}")
    brackets = [r for r in rows if r[1] == 'BRACKET']
    print(f"BRACKETS detected: {len(brackets)}")
    print("top 10 true best-ask totals (sum = minYesAsk + minNoAsk):")
    for total, kind, yp, np, q, liq, sh, edge in rows[:10]:
        print(f"  {total:.4f} [{kind}] Yes@{yp:.3f} No@{np:.3f} liq={liq} | {q}")

asyncio.run(scan())
