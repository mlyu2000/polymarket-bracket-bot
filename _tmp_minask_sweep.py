import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from models import Market, OrderBook

logging.basicConfig(level=logging.ERROR)

async def sweep():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    elapsed = time.time() - t0

    near = []
    best = []
    zero_liq = 0
    dead = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        # liquidity / activity guards (mirror detector)
        if not yes_book or not no_book:
            zero_liq += 1; continue
        if not yes_book.asks or not no_book.asks:
            zero_liq += 1; continue
        if not m.active or m.closed:
            dead += 1; continue
        if m.liquidity <= 0 or m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        # TRUE best ask via min() (correct) vs asks[0] (artifact)
        y_best = min(yes_book.asks, key=lambda a: float(a["price"]))
        n_best = min(no_book.asks, key=lambda a: float(a["price"]))
        yp = float(y_best["price"]); np = float(n_best["price"])
        total = yp + np
        if total <= 1.005:
            near.append((total, yp, np, m.liquidity, m.question[:55]))
        # raw asks[0] for the artifact comparison
        yp0 = float(yes_book.asks[0]['price']); np0 = float(no_book.asks[0]['price'])
        t0_sum = yp0 + np0
        best.append((total, t0_sum))

    near.sort()
    print(f"🔧 Min-ask near-miss sweep: {len(markets)} markets in {elapsed:.1f}s")
    print(f"   dead/closed skipped: {dead}, zero-liq/skipped books: {zero_liq}")
    print(f"   ✅ Near-misses (min-ask, sum≤1.005): {len(near)}")
    for total, yp, np, liq, q in near[:10]:
        print(f"   min {total:.4f} | Yes@{yp:.4f} No@{np:.4f} | liq=${liq:,.0f} | {q}")

    # artifact demonstration: asks[0] sums
    min_sum = min(b[0] for b in best) if best else 9
    artifact_max = max(b[1] for b in best) if best else 9
    print(f"   📉 True min two-sided ask = {min_sum:.4f}")
    print(f"   📈 asks[0] artifact max sum = {artifact_max:.4f} (this is why the script's near-miss list was empty)")
    if near:
        print(f"   → lowest real sum {near[0][0]:.4f} is {'≤1.005 (near-miss)' if near[0][0] <= 1.005 else '>1.005'}")
    else:
        print(f"   → even the true min ask {min_sum:.4f} exceeds 1.005 — no near-misses exist")

asyncio.run(sweep())
