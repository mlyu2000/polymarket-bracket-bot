import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    brackets = []
    near = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append((opp.total_cost, opp.net_edge, opp.max_shares, opp.yes_price, opp.no_price, m.question[:60], m.liquidity))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            if total < 1.0:
                near.append(('BRACKET(best-ask)', total, m.question[:55], yp, np, m.liquidity))
            elif total <= 1.005:
                near.append(('near', total, m.question[:55], yp, np, m.liquidity))
    near.sort(key=lambda x: x[1])
    print(f"priced markets: {priced} / {len(markets)} in {scan_time:.1f}s")
    print(f"detector brackets: {len(brackets)}")
    for b in brackets:
        print(f"  {b[0]:.3f} edge={b[1]:.4f} shares={b[2]} Y@{b[3]:.3f} N@{b[4]:.3f} liq={b[6]} | {b[5]}")
    print(f"best-ask sum<1.005: {len(near)}")
    for t in near[:10]:
        print(f"  {t[0]} {t[1]:.4f} | Y@{t[3]:.3f} N@{t[4]:.3f} liq={t[5]} | {t[2]}")

asyncio.run(scan())
