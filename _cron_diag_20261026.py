"""Supplementary min-ask diagnostic to verify near-miss accuracy."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    elapsed = time.time() - t0

    # Use min-ask (correct) for both-sided sums
    min_ask_sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_min = min(float(a['price']) for a in yes_book.asks)
            no_min = min(float(a['price']) for a in no_book.asks)
            total = yes_min + no_min
            min_ask_sums.append((total, m.question[:60], yes_min, no_min, m.liquidity))

    min_ask_sums.sort()
    below_105 = [s for s in min_ask_sums if s[0] <= 1.005]
    two_sided_below_1005 = len(below_105)

    print(f"🔍 Min-ask diagnostic: {len(markets)} markets in {elapsed:.1f}s")
    print(f"📊 Two-sided min-ask sums ≤ 1.005: {two_sided_below_1005}")
    print(f"📉 Lowest 5 min-ask sums:")
    for total, q, yp, np, liq in min_ask_sums[:5]:
        print(f"  {total:.4f} | Yes@{yp:.4f} No@{np:.4f} | liq={liq:.0f} | {q}")
    # Tier breakdown
    tiers = {
        'le1.000': sum(1 for s in min_ask_sums if s[0] < 1.000),
        'le1.005': sum(1 for s in min_ask_sums if s[0] <= 1.005),
        'le1.010': sum(1 for s in min_ask_sums if s[0] <= 1.010),
        'le1.020': sum(1 for s in min_ask_sums if s[0] <= 1.020),
        'le1.050': sum(1 for s in min_ask_sums if s[0] <= 1.050),
    }
    print(f"📈 Tiers: {tiers}")

asyncio.run(main())
