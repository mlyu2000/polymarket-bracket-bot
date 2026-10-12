import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    if not book or not getattr(book, 'asks', None):
        return None
    return min(float(a['price']) for a in book.asks)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    totals = []
    brackets = []
    for m, (yb, nb) in zip(markets, all_books):
        ya, na = best_ask(yb), best_ask(nb)
        if ya is None or na is None:
            continue
        s = ya + na
        totals.append((s, m.question[:60], ya, na, m.liquidity))
        if s < 1.0:
            brackets.append((s, m.question[:60], ya, na, m.liquidity))
    totals.sort()
    return markets, totals, brackets

markets, totals, brackets = asyncio.run(scan())
print(f"markets={len(markets)} priced={len(totals)}")
print(f"TRUE_BRACKETS(min-ask sum<1.00): {len(brackets)}")
for s, q, ya, na, liq in sorted(brackets):
    print(f"  BRACKET {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
print("BOTTOM 10 by min-ask sum:")
for s, q, ya, na, liq in totals[:10]:
    print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
print(f"near-misses <=1.005: {sum(1 for t in totals if t[0] <= 1.005)}")
