import json

lines = [l for l in open('results/cron_scan_history.jsonl') if l.strip()]
prev = json.loads(lines[-2])
cur = json.loads(lines[-1])
prev_full = {t[1][:50]: t[1] for t in prev['near_1.000_1.005']}
cur['near_1.000_1.005'] = [[s, prev_full.get(q, q), y, n, l] for s, q, y, n, l in cur['near_1.000_1.005']]
cur['note'] = cur['note'].replace(
    "Band 6->6 (names truncated [:50] this run): adds ['Exact Score: West Ham United FC 0 - 3 Queens Park ', 'Exact Score: Racing Club de Lens 0 - 4 Olympique L', 'Gimnasia y Esgrima de La Plata vs. CA Tucum\\u00e1n: O/U', \"FC Sochaux-Montb\\u00e9liard vs. US Boulogne C\\u00f4te d'Opal\"], drops ['Exact Score: West Ham United FC 0 - 3 Queens Park Rangers FC', 'Exact Score: Racing Club de Lens 0 - 4 Olympique Lyonnais?', 'Gimnasia y Esgrima de La Plata vs. CA Tucum\\u00e1n: O/U 7.5', \"FC Sochaux-Montb\\u00e9liard vs. US Boulogne C\\u00f4te d'Opale: O/U 6.5\"]. Intra-band shifts: none.",
    "Band 6->6: adds [], drops []. Intra-band shifts: Lens 0-4 Lyon Yes@0.012/No@0.992 -> Yes@0.013/No@0.991 (sum unchanged 1.004)."
)
lines[-1] = json.dumps(cur)
open('results/cron_scan_history.jsonl', 'w').write('\n'.join(lines) + '\n')
print('band:')
for t in cur['near_1.000_1.005']:
    print(' ', t)
print('note:', cur['note'])
