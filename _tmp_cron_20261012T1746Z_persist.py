import json

entry = {
    'ts_utc': '2026-10-12T1746Z',
    'markets': 500,
    'scan_time_s': 54.2,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 73,
    'best_ask_floor': 1.005,
    'near_1.000_1.005': [
        [1.0050, 'Spread: Galatasaray SK (-2.5)', 0.015, 0.990, 19016.26091],
        [1.0060, 'Real Oviedo vs. SD Eibar: Real Oviedo O/U 4.5', 0.014, 0.992, 1803.48],
        [1.0060, 'Will the Democratic Party win the NH-02 House seat', 0.954, 0.052, 50786.43568],
        [1.0070, 'Spread: SK Slovan Bratislava (-2.5)', 0.008, 0.999, 20340.11765],
        [1.0090, 'Will the highest temperature in Amsterdam be 13C on October 14?', 0.010, 0.999, 2503.84437],
    ],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "Floor LOOSENED 1.0010 -> 1.0050 since 1728Z: the 1728Z all-time-low-tie market (Flavio Bolsonaro 2nd-round "
             "win-margin 8-12%, Y@0.146 N@0.855 liq 94.8k) now has NO asks on either side (verified directly via gamma "
             "event 1138953 + CLOB book: both books empty of asks; outcomePrices still 0.1455/0.8545) so it can no longer "
             "be bracket-bought and drops out of the two-sided set; KFUM Oslo/Vaalerenga 1.0020 also dropped out of the "
             "band. Floor reverts to Galatasaray SK (-2.5) 1.0050 HELD (liq 23.7k -> 19.0k) SOLO; band <=1.005 n=1 (was 3). "
             "NEW band member Real Oviedo vs. SD Eibar O/U 4.5 1.0060 (thin, liq 1.8k); NH-02 1.0060 (tightened from "
             "1.0070, liq 50.8k); SK Slovan Bratislava 1.0070 held. tiers <=1.005 n=1 <=1.010 n=13 <=1.020 n=25 "
             "<=1.030 n=30 <=1.050 n=43. 73 two-sided / 418 yes-only / 1 no-only / 8 empty = 84.8% not bracket-able "
             "(excluding empty: 85.9%). detector-opps 0, paper 0 executions; no sum < 1.00 anywhere = zero positive gross "
             "edge; floor 1.0050, best gross edge -0.0050, still 0.025 above the 0.98 actionable threshold. NOT actionable."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', entry['ts_utc'], '| floor', entry['best_ask_floor'], '| brackets', entry['brackets_verbatim'])
