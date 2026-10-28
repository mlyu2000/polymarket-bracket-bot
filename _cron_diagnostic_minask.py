"""Diagnostic: near-misses using correct min-ask (best ask), vs asks[0] artifact."""
import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI
from models import Market, OrderBook

logging_ok = True

async def main():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    minask_near = []   # correct: min ask on each side
    asks0_near = []    # artifact: asks[0] (worst ask if descending)
    floors = []
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        y_min = min(yb.asks, key=lambda a: float(a["price"]))
        n_min = min(nb.asks, key=lambda a: float(a["price"]))
        yp, np = float(y_min["price"]), float(n_min["price"])
        total = yp + np
        floors.append(total)
        if total <= 1.005:
            minask_near.append((total, m.question[:55], yp, np, m.liquidity))
        y0 = float(yb.asks[0]["price"])
        n0 = float(nb.asks[0]["price"])
        if y0 + n0 <= 1.005:
            asks0_near.append((y0+n0, m.question[:55], y0, n0, m.liquidity))

    floors.sort()
    print(f"🔍 Scan: {len(markets)} markets in {dt:.1f}s")
    print(f"🏦 Min-liquidity-skipped: {sum(1 for m in markets if m.liquidity < Config.MIN_LIQUIDITY_USDC)}")
    print(f"📈 Floor (min total) across all markets: {floors[0]:.3f}")
    print(f"📈 Median total: {floors[len(floors)//2]:.3f}")
    print(f"📊 NEAR-MISSES min-ask (<=1.005): {len(minask_near)}")
    for total, q, yp, np, liq in minask_near[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq=${liq:,.0f} | {q}")
    print(f"📉 Near-misses asks[0] (<=1.005): {len(asks0_near)}  ← artifact: asks[0] may be worst ask")

asyncio.run(main())
