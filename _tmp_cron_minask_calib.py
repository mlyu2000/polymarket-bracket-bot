"""Min-ask calibration scan — source of truth for true best-ask floor.

asks[0] near-miss block in run_scan.py is a known DESC-sort artifact (only
catches degenerate single-level books; volatile 0..24 between runs). This
script uses min(all asks) per leg, matching detector.py and the persisted
supp scans.
"""
import asyncio, logging, json, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []            # (total, q, yes_min, no_min, liq, has_min_liq, min_liquidity_usdc)
    brackets = []        # real min-based brackets (net edge >= MIN_PROFIT_MARGIN)
    two_sided = 0
    yes_only = 0
    na_only = 0
    unpriced = 0

    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb):
            unpriced += 1
            continue
        if not (yb.asks and nb.asks):
            if yb.asks and not nb.asks:
                yes_only += 1
            elif nb.asks and not yb.asks:
                na_only += 1
            else:
                unpriced += 1
            continue
        two_sided += 1
        ymin = min(float(a['price']) for a in yb.asks)
        nmin = min(float(a['price']) for a in nb.asks)
        total = ymin + nmin
        below = m.liquidity < Config.MIN_LIQUIDITY_USDC
        rows.append((total, m.question[:55], ymin, nmin, m.liquidity, below,
                     Config.MIN_LIQUIDITY_USDC))
        # Real bracket check via the (correct, min-based) detector
        opp = detector.detect(m, yb, nb)
        if opp:
            brackets.append({
                'q': m.question[:90], 'yes': opp.yes_price, 'no': opp.no_price,
                'sum': round(opp.total_cost, 4), 'edge': round(opp.net_edge, 5),
                'shares': opp.max_shares, 'liq': m.liquidity,
            })

    rows.sort(key=lambda r: r[0])
    ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())

    all_total = [r[0] for r in rows]
    priced_total = [r[0] for r in rows if not r[5]]  # above MIN_LIQ guard
    sup_total = [r[0] for r in rows if r[5]]          # below MIN_LIQ (sups)

    tiers_all = {
        'lt_1_000': sum(1 for r in all_total if r < 1.000),
        'le_1_005': sum(1 for r in all_total if r <= 1.005),
        'le_1_010': sum(1 for r in all_total if r <= 1.010),
        'le_1_020': sum(1 for r in all_total if r <= 1.020),
        'le_1_050': sum(1 for r in all_total if r <= 1.050),
    }
    tiers_liq = {
        'lt_1_000': sum(1 for r in priced_total if r < 1.000),
        'le_1_005': sum(1 for r in priced_total if r <= 1.005),
        'le_1_010': sum(1 for r in priced_total if r <= 1.010),
        'le_1_020': sum(1 for r in priced_total if r <= 1.020),
        'le_1_050': sum(1 for r in priced_total if r <= 1.050),
    }
    sup_tiers = {
        'lt_1_000': sum(1 for r in sup_total if r < 1.000),
        'le_1_005': sum(1 for r in sup_total if r <= 1.005),
        'le_1_050': sum(1 for r in sup_total if r <= 1.050),
    }

    floor = rows[0][0] if rows else None
    leader = rows[0] if rows else None

    print('=' * 70)
    print('MIN-ASK CALIBRATION SCAN (source of truth — min(all asks) per leg)')
    print('=' * 70)
    print(f"TS: {ts} | markets={len(markets)} | scan_time={scan_time:.1f}s")
    print(f"min_liquidity_guard={Config.MIN_LIQUIDITY_USDC} | "
          f"min_profit_margin={Config.MIN_PROFIT_MARGIN}")
    print(f"two_sided={two_sided} yes_only={yes_only} na_only={na_only} "
          f"unpriced={unpriced} not_bracketable={len(markets)-two_sided} "
          f"({(len(markets)-two_sided)/len(markets)*100:.1f}%)")
    print()
    print(f"REAL BRACKETS (min-based, net_edge>=margin, liq>={Config.MIN_LIQUIDITY_USDC}): "
          f"{len(brackets)}")
    for b in brackets:
        print(f"  BRACKET {b['sum']:.4f} (edge={b['edge']:.4f}) | "
              f"Yes@{b['yes']:.3f} No@{b['no']:.3f} | {b['q']}")
    print()
    print("TIERS (min-ask sum, ALL two-sided markets):")
    print(f"  {tiers_all}")
    print("TIERS (min-ask sum, above MIN_LIQUIDITY guard):")
    print(f"  {tiers_liq}")
    print("TIERS (min-ask sum, BELOW MIN_LIQUIDITY guard — sup/low-liq):")
    print(f"  {sup_tiers}")
    print()
    print(f"FLOOR (min-ask) = {floor:.4f}" if floor else "FLOOR = n/a")
    if leader:
        print(f"  leader: {leader[1][:55]} | Y{leader[2]:.3f} N{leader[3]:.3f} "
              f"liq={leader[4]:,.1f} min_liq_guard={leader[4] < Config.MIN_LIQUIDITY_USDC}")
    print()
    print("TOP-15 near-parity (min-ask, above MIN_LIQ guard):")
    cnt = 0
    for r in rows:
        if cnt >= 15:
            break
        total, q, ymin, nmin, liq, below, ml = r
        if below:
            continue
        cnt += 1
        print(f"  {total:.4f} | Y{ymin:.3f} N{nmin:.3f} | liq={liq:,.1f} | {q[:55]}")
    print()
    print("TOP-8 below MIN_LIQUIDITY guard (sup, min-ask):")
    cnt = 0
    for r in rows:
        if cnt >= 8:
            break
        total, q, ymin, nmin, liq, below, ml = r
        if not below:
            continue
        cnt += 1
        print(f"  {total:.4f} | Y{ymin:.3f} N{nmin:.3f} | liq={liq:,.1f} (<{ml}) | {q[:55]}")

    # JSON record (persisted locally, unpushed per project rule)
    out = {
        'ts': ts, 'markets': len(markets), 'scan_time': round(scan_time, 1),
        'min_liquidity_guard': Config.MIN_LIQUIDITY_USDC,
        'min_profit_margin': Config.MIN_PROFIT_MARGIN,
        'two_sided': two_sided, 'yes_only': yes_only, 'na_only': na_only,
        'not_bracketable': len(markets) - two_sided,
        'bracketable_pct': round((two_sided / len(markets) * 100), 1),
        'brackets': brackets,
        'floor_min_ask': round(floor, 4) if floor else None,
        'leader': {'q': leader[1], 'yes': leader[2], 'no': leader[3],
                   'liq': leader[4]} if leader else None,
        'tiers_all_two_sided': tiers_all,
        'tiers_above_min_liq': tiers_liq,
        'tiers_below_min_liq': sup_tiers,
        'top15_above_min_liq': [
            {'total': round(r[0], 4), 'q': r[1], 'yes': r[2], 'no': r[3],
             'liq': r[4]} for r in rows if not r[5]][:15],
        'top8_below_min_liq': [
            {'total': round(r[0], 4), 'q': r[1], 'yes': r[2], 'no': r[3],
             'liq': r[4]} for r in rows if r[5]][:8],
    }
    with open(f'runs/_tmp_cron_{ts}_supp_data.json', 'w') as f:
        json.dump(out, f, indent=2)
    print()
    print(f"[persisted] runs/_tmp_cron_{ts}_supp_data.json")

asyncio.run(scan())
