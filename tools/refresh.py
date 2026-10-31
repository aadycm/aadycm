# daily refresh run by .github/workflows/refresh-heatmap.yml
# fetches the calendar and rebuilds with the next asset version only if the activity changed
# the calendar window rolls forward every day so comparing the whole file would commit daily for nothing
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, 'contrib.json')


def active(text):
    return {(d['date'], d['count']) for d in json.loads(text) if d['count']}


before = open(DATA, encoding='utf8').read()
subprocess.run([sys.executable, os.path.join(HERE, 'fetch_contributions.py')], check=True)
after = open(DATA, encoding='utf8').read()

if active(before) == active(after):
    open(DATA, 'w', encoding='utf8').write(before)
    print('no new activity so nothing to rebuild')
    sys.exit(0)

readme = open(os.path.join(ROOT, 'README.md'), encoding='utf8').read()
version = max(int(v) for v in re.findall(r'\?v=(\d+)', readme)) + 1
subprocess.run([sys.executable, os.path.join(HERE, 'build.py'), str(version)], check=True)
print('rebuilt at version', version)
