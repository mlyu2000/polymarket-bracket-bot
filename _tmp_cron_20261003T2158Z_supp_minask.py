import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    both_priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        both_priced += 1
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        ya = min(yb.asks, key=lambda a: float(a['price']))
        na = min(nb.asks, key=lambda a: float(a['price']))
        yp, np_ = float(ya['price']), float(na['price'])
        if yp <= 0 or np_ <= 0 or yp >= 1 or np_ >= 1:
            continue
        rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))

    rows.sort()
    print(f"both-sides-priced: {both_priced}/{len(markets)}")
    print("TOP 10 min-ask totals:")
    for t, q, yp, np_, liq in rows[:10]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    n1005 = [r for r in rows if r[0] <= 1.005]
    n1010 = [r for r in rows if r[0] <= 1.010]
    print(f"count<=1.005: {len(n1005)} | count<=1.010: {len(n1010)} | floor: {rows[0][0]:.4f}")

asyncio.run(supp())
