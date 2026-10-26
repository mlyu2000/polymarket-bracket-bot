import asyncio, logging, json, collections
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    brackets = []
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            brackets.append({
                'q': m.question[:70],
                'yes': round(opp.yes_price, 4),
                'no': round(opp.no_price, 4),
                'sum': round(opp.total_cost, 4),
                'edge': round(opp.net_edge, 4),
                'shares': opp.max_shares,
                'liq': round(m.liquidity, 1),
            })
        if yb and nb and yb.asks and nb.asks:
            ymin = min(float(a['price']) for a in yb.asks)
            nmin = min(float(a['price']) for a in nb.asks)
            rows.append((ymin + nmin, m.question[:60], ymin, nmin, m.liquidity, bool(opp)))
    rows.sort()

    lt1 = [r for r in rows if r[0] < 1.0]
    le1005 = [r for r in rows if r[0] <= 1.005]
    le1010 = [r for r in rows if r[0] <= 1.010]
    le1020 = [r for r in rows if r[0] <= 1.020]
    le1050 = [r for r in rows if r[0] <= 1.050]
    two_sided = sum(1 for r in rows if r[5])

    print(f"two-sided markets (book-able pairs): {len(rows)}")
    print(f"min-ask sum < 1.00 (true brackets): {len(lt1)}")
    print(f"<= 1.005: {len(le1005)} | <= 1.010: {len(le1010)} | <= 1.020: {len(le1020)} | <= 1.050: {len(le1050)}")
    print(f"floor: {rows[0][0]:.4f} | {rows[0][1]} (liq {rows[0][4]:.1f})")
    print("--- top 10 by min-ask sum ---")
    for r in rows[:10]:
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq {r[4]:.1f} | {r[1]}")
    print("--- brackets (detector) ---")
    print(json.dumps(brackets, indent=2))
    print("--- data for persistence ---")
    print("ROWS_JSON:" + json.dumps([[round(r[0],4), r[1], round(r[2],4), round(r[3],4), round(r[4],1), r[5]] for r in rows]))
    print("BRACKETS_JSON:" + json.dumps(brackets))
    print(f"STATS: two_sided={len(rows)} lt1={len(lt1)} le1005={len(le1005)} le1010={len(le1010)} le1020={len(le1020)} le1050={len(le1050)} floor={rows[0][0]:.4f}")

asyncio.run(scan())
