import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        ya = min(yb.asks, key=lambda a: float(a["price"]))
        na = min(nb.asks, key=lambda a: float(a["price"]))
        yp, np_ = float(ya["price"]), float(na["price"])
        if yp <= 0 or np_ <= 0 or yp >= 1 or np_ >= 1:
            continue
        priced += 1
        rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity,
                     int(float(ya["size"])), int(float(na["size"]))))
    rows.sort()
    print(f"[min-ask supplement] {len(markets)} markets, {priced} priced, {dt:.1f}s")
    print("-- top 12 by min-ask sum --")
    for s, q, yp, np_, liq, ys, ns in rows[:12]:
        flag = "BRACKET<1" if s < 1.0 else ("near<=1.005" if s <= 1.005 else "")
        print(f"  {s:.3f} | Y@{yp:.3f} N@{np_:.3f} | liq={liq:.0f} sz={ys}/{ns} | {flag} | {q}")

asyncio.run(scan())
