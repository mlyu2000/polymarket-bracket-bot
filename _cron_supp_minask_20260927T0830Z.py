"""Supplemental near-miss check using BEST ask (min price), since the CLOB
payload lists asks in DESC order and asks[0] is the worst ask. Uses the same
detector guards (active, liq>0, min liquidity, prices in (0,1))."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    print(f"fetch time {time.time()-t0:.1f}s, {len(markets)} markets")

    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        if not m.active or m.closed or m.liquidity <= 0 or m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        ya = min(yb.asks, key=lambda a: float(a['price']))
        na = min(nb.asks, key=lambda a: float(a['price']))
        yp, np_ = float(ya['price']), float(na['price'])
        if yp <= 0 or np_ <= 0 or yp >= 1 or np_ >= 1:
            continue
        total = yp + np_
        shares = min(int(float(ya['size'])), int(float(na['size'])))
        rows.append((total, m.question[:60], yp, np_, m.liquidity, shares))

    rows.sort()
    print(f"priced markets: {len(rows)}")
    print("--- 12 lowest best-ask sums ---")
    for total, q, yp, np_, liq, sh in rows[:12]:
        flag = " <1.00!" if total < 1.0 else ""
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:,.0f} | bestQ={sh} | {q}{flag}")
    floor = rows[0][0] if rows else None
    print(f"FLOOR: {floor}")

asyncio.run(main())
