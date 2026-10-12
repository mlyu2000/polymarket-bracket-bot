import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_misses = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60],
                'yes': opp.yes_price,
                'no': opp.no_price,
                'sum': opp.total_cost,
                'edge': opp.net_edge,
                'shares': opp.max_shares,
                'liq': m.liquidity
            })
            paper_result = paper.execute(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print('\nScan: {} markets in {:.1f}s'.format(result["markets"], result["scan_time"]))
print('✅ BRACKETS (sum < 1.00): {}'.format(len(result["opps"])))
print('📊 Near-misses (≤1.005): {}'.format(len(result["near_misses"])))

if result['opps']:
    print('\n=== 🚨 ACTIONABLE BRACKETS (sum < 1.00) ===')
    for o in result['opps']:
        print('\n⊕ Sum: {:.3f} | Edge: {:.4f} | Max Shares: {}'.format(o["sum"], o["edge"], o["shares"]))
        print('+ Yes @ {:.3f} | No @ {:.3f} | Liquidity: {}'.format(o["yes"], o["no"], o["liq"]))
        print('+ Question: {}...'.format(o["q"]))
        print('+ ETH: ${:.2f}'.format(o["edge"]*o["shares"]))

if result['near_misses'][:5]:
    print('\n=== 🕐 NEAR-MISSES (≤1.005) ===')
    for total, q, yp, np, liq in result['near_misses'][:5]:
        print('+ {:.3f} | Yes@{:3} No@{:3} | {}...'.format(total, yp, np, q))
