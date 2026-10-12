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

    # Correct near-miss/floor math: CLOB asks are DESC-sorted, best ask = min price.
    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        if yp <= 0 or np <= 0 or yp >= 1 or np >= 1:
            continue
        priced += 1
        total = yp + np
        gross = 1.0 - total
        net = gross - Config.FEE_BUFFER - Config.SLIPPAGE_BUFFER
        rows.append((total, m.question[:58], yp, np, m.liquidity, net, m.slug))

    rows.sort()
    print(f"🔍 Corrected scan: {len(markets)} markets in {scan_time:.1f}s | priced pairs: {priced}")
    print(f"✅ TRUE BRACKETS (best-ask sum < 1.00): {sum(1 for r in rows if r[0] < 1.0)}")
    for r in rows:
        if r[0] < 1.0:
            print(f"  🔴 sum={r[0]:.4f} net={r[5]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq=${r[4]:,.0f} | {r[1]}")
    print(f"📊 TOP 10 CLOSEST (best-ask sum, any value):")
    for total, q, yp, np, liq, net, slug in rows[:10]:
        print(f"  {total:.4f} (net={net:.4f}) | Yes@{yp:.3f} No@{np:.3f} | liq=${liq:,.0f} | {q}")
    if rows:
        print(f"📉 Floor (min best-ask sum observed): {rows[0][0]:.4f}")
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"📊 Near-misses with corrected math (1.000 < sum <= 1.005): {len(nm)}")
    for total, q, yp, np, liq, net, slug in nm[:5]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq=${liq:,.0f} | {q}")

asyncio.run(scan())
