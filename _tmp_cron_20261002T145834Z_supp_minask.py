import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    priced = 0
    brackets = []
    near = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            near.append((total, m.question[:60], yp, np_, m.liquidity))
    near.sort()
    print(f"Markets: {len(markets)} | priced (both best asks): {priced} | scan {scan_time:.1f}s")
    print(f"Detector brackets: {len(brackets)}")
    for b in brackets:
        print(f"  BRACKET sum={b.total_cost:.4f} edge={b.net_edge:.4f} yes={b.yes_price:.3f} no={b.no_price:.3f} shares={b.max_shares}")
    print("Best min-ask sums (true floor):")
    for total, q, yp, np_, liq in near[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"Sums < 1.00: {sum(1 for t,*_ in near if t < 1.0)}")
    print(f"Sums <= 1.005: {sum(1 for t,*_ in near if t <= 1.005)}")
    print(f"Sums <= 1.01: {sum(1 for t,*_ in near if t <= 1.01)}")

asyncio.run(scan())
