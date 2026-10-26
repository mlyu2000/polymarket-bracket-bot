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
    scan_time = time.time() - t0
    print(f"🔍 {len(markets)} markets, {len(all_books)} books in {scan_time:.1f}s")

    both_ask_markets = 0
    sums_minask = []  # min(all asks) — source of truth
    sums_asks0 = []   # asks[0] — the artifact-prone version
    best_brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        both_ask_markets += 1
        # min-ask (correct)
        yp = float(min(yes_book.asks, key=lambda a: float(a["price"]))["price"])
        np = float(min(no_book.asks, key=lambda a: float(a["price"]))["price"])
        s_min = yp + np
        sums_minask.append((s_min, yp, np, m.question[:50]))
        # asks[0] (artifact-prone)
        yp0 = float(yes_book.asks[0]["price"])
        np0 = float(no_book.asks[0]["price"])
        s_0 = yp0 + np0
        sums_asks0.append(s_0)
        best_brackets.append((s_min, m.question[:50], yp, np, m.liquidity))

    sums_minask.sort(key=lambda x: x[0])
    sums_asks0.sort()
    import statistics
    print(f"  markets with both-side asks: {both_ask_markets}")
    print(f"  --- min-ask (correct) sums ---")
    print(f"  min={min(s[0] for s in sums_minask):.4f}  median={statistics.median(s[0] for s in sums_minask):.4f}  max={max(s[0] for s in sums_minask):.4f}")
    print(f"  brackets (sum<1.00): {sum(1 for s in sums_minask if s[0] < 1.00)}")
    print(f"  near-miss (sum<=1.005): {sum(1 for s in sums_minask if s[0] <= 1.005)}")
    print(f"  near-miss (sum<=1.010): {sum(1 for s in sums_minask if s[0] <= 1.010)}")
    q = min(int(len(sums_minask)*0.1), 10)
    print(f"  10 cheapest by min-ask:")
    for s, yp, np, question in sums_minask[:10]:
        print(f"    {s:.4f}  Yes@{yp:.3f} No@{np:.3f} | {question}")
    print(f"  --- asks[0] (artifact-prone) sums ---")
    print(f"  min={min(sums_asks0):.4f}  median={statistics.median(sums_asks0):.4f}  max={max(sums_asks0):.4f}")

asyncio.run(main())
