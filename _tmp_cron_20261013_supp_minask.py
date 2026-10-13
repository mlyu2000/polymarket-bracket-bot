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

    brackets = []
    two_sided = []
    yes_only = 0
    no_asks_only = 0
    bands = {'le1.002':0,'le1.005':0,'le1.010':0,'le1.020':0,'le1.030':0}
    best = None  # (total, q, yp, np)

    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book):
            continue
        y_asks = yes_book.asks or []
        n_asks = no_book.asks or []
        if not y_asks:
            no_asks_only += 1
            continue
        if not n_asks:
            yes_only += 1
            continue
        yp = min(float(a['price']) for a in y_asks)
        np_ = min(float(a['price']) for a in n_asks)
        total = yp + np_
        two_sided.append((total, m.question[:50], yp, np_, m.liquidity))
        if total < 1.0:
            brackets.append((total, m.question[:50], yp, np_, m.liquidity))
        if best is None or total < best[0]:
            best = (total, m.question[:50], yp, np_, m.liquidity)
        if total <= 1.002: bands['le1.002'] += 1
        if total <= 1.005: bands['le1.005'] += 1
        if total <= 1.010: bands['le1.010'] += 1
        if total <= 1.020: bands['le1.020'] += 1
        if total <= 1.030: bands['le1.030'] += 1

    two_sided.sort()
    totals = [t[0] for t in two_sided]
    n = len(totals)
    median = totals[n//2] if n else None

    print(f"🔍 Scan: {len(markets)} markets in {scan_time:.1f}s")
    print(f"✅ TRUE BRACKETS (min-ask sum < 1.00): {len(brackets)}")
    for total, q, yp, np_, liq in brackets[:10]:
        print(f"  🔴 {total:.4f} | Yes@{yp:.4f} No@{np_:.4f} | liq={liq} | {q}")
    print(f"📊 Market structure:")
    print(f"  two-sided (both Y&N asks): {n} / {len(markets)}")
    print(f"  yes-only (no N asks): {yes_only}")
    print(f"  no-asks (no Y asks): {no_asks_only}")
    if n:
        pct = 100.0*(len(markets)-n)/len(markets)
        print(f"  not bracketable (missing a side): {pct:.1f}%")
        print(f"📉 2-sided min-ask floor: {best[0]:.4f} | {best[1]} (Y@{best[2]:.4f} N@{best[3]:.4f})" if best else "  no floor")
        print(f"📊 median 2-sided min-ask: {median:.4f}" if median else "  no median")
    print(f"📊 bands (of two-sided): {bands}")
    print(f"📋 Closest 5 two-sided (min-ask):")
    for total, q, yp, np_, liq in two_sided[:5]:
        print(f"  {total:.4f} | Yes@{yp:.4f} No@{np_:.4f} | {q}")

asyncio.run(scan())
