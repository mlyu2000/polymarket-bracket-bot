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

    # True best asks are min(asks) — CLOB /book lists asks DESC-sorted,
    # so asks[0] is the worst ask (~0.999) and never triggers the near-miss band.
    opps = []
    near = []
    floor = None
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            if yp <= 0 or yp >= 1 or np_ <= 0 or np_ >= 1:
                continue
            total = yp + np_
            priced += 1
            if floor is None or total < floor[0]:
                floor = (total, m.question[:50], yp, np_, m.liquidity)
            if total <= 1.005 and m.liquidity >= Config.MIN_LIQUIDITY_USDC:
                near.append((total, m.question[:50], yp, np_, m.liquidity))

    near.sort()
    print(f"⏱ min-ask scan: {len(markets)} markets ({priced} priced) in {scan_time:.1f}s")
    print(f"✅ BRACKETS (detector, net_edge >= margin): {len(opps)}")
    for o in opps:
        print(f"  🔴 sum={o.total_cost:.4f} edge={o.net_edge:.4f} | Yes@{o.yes_price:.3f} No@{o.no_price:.3f} | {o.max_shares} shares")
    print(f"📊 Near-misses (min-ask ≤ 1.005): {len(near)}")
    for total, q, yp, np_, liq in near[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    if floor:
        print(f"📉 Best-ask floor: {floor[0]:.4f} | Yes@{floor[2]:.3f} No@{floor[3]:.3f} | {floor[1]}")

result = asyncio.run(scan())
