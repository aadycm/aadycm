# refreshes tools/contrib.json from the public contribution calendar
# usage  python tools/fetch_contributions.py  then rebuild with a new asset version
import json, os, re, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
USER = 'aadycm'

html = urllib.request.urlopen(f'https://github.com/users/{USER}/contributions').read().decode()
days = {}
for m in re.finditer(r'data-date="([\d-]+)" id="(contribution-day-component-\d+-\d+)" data-level="(\d)"', html):
    days[m.group(2)] = {'date': m.group(1), 'level': int(m.group(3)), 'count': 0}
# the counts only live in the tooltip text next to each square
for m in re.finditer(r'for="(contribution-day-component-\d+-\d+)"[^>]*>([^<]*)', html):
    n = re.match(r'([\d,]+) contribution', m.group(2))
    if m.group(1) in days and n:
        days[m.group(1)]['count'] = int(n.group(1).replace(',', ''))
out = sorted(days.values(), key=lambda d: d['date'])
assert len(out) > 300, 'calendar markup changed and nothing was parsed'
json.dump(out, open(os.path.join(HERE, 'contrib.json'), 'w'))
print(len(out), 'days', sum(d['count'] for d in out), 'contributions')
