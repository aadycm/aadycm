<!-- ────────────────────────────────────────────────────────────────
     Rebuild the SVGs after any edit:  sh build.sh
     Setup + checklist: SETUP.md
     ──────────────────────────────────────────────────────────── -->

<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="assets/hero-light.svg?v=6">
  <img src="assets/hero.svg?v=6" alt="Aadithya Chandramouli — CS senior at Penn State, building AI systems." width="100%">
</picture>
</p>

<table>
<tr>
<td width="50%">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/identity.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="assets/identity-light.svg?v=6">
  <img src="assets/identity.svg?v=6" alt="Aadithya Chandramouli, 4th-year Computer Science and Learning Assistant at Penn State University, India." width="100%">
</picture>
</td>
<td width="50%">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/now.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="assets/now-light.svg?v=6">
  <img src="assets/now.svg?v=6" alt="Right now: teaching HydroNode to look at the plants. Figuring out: how small a model can get on a board with no GPU." width="100%">
</picture>
</td>
</tr>
</table>

I'm a computer science senior at Penn State, and a Learning Assistant there. Most of what I
build ends up being machine learning plus everything around it — the sensors, the pipeline, the
API, the dashboard someone actually opens. The model is usually the part that takes the least
time.

- Most of my projects started because something annoyed me. HydroNode exists because I got
  tired of plants dying while I was away.
- I'd rather have something rough running this week than something perfect next month. The
  rough version is what tells you which half of the plan was wrong.
- I've spent enough nights chasing a crash that turned out to be a loose wire to care a lot
  about logs, watchdogs, and things that fail loudly.

<img src="assets/divider.svg?v=6" alt="" width="100%">

## Stack

<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/stack.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="assets/stack-light.svg?v=6">
  <img src="assets/stack.svg?v=6" alt="Stack — languages, AI and ML, backend, frontend, data, infrastructure" width="100%">
</picture>
</p>

<img src="assets/divider.svg?v=6" alt="" width="100%">

## Selected Work

<table>
<tr>
<td width="50%">
<a href="https://hydronode.in">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/tiles/hydronode.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="assets/tiles/hydronode-light.svg?v=6">
  <img src="assets/tiles/hydronode.svg?v=6" alt="HydroNode — five growing systems, each running its own controller. Live at hydronode.in." width="100%">
</picture>
</a>
</td>
<td width="50%">
<a href="https://github.com/aadycm/semantic-notes">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/tiles/semantic.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="assets/tiles/semantic-light.svg?v=6">
  <img src="assets/tiles/semantic.svg?v=6" alt="Semantic Notes — two versions of the same search, 88.6 percent against 85.7 percent recall at one." width="100%">
</picture>
</a>
</td>
</tr>
<tr>
<td width="50%">
<a href="https://github.com/aadycm/paper-trail">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/tiles/papertrail.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="assets/tiles/papertrail-light.svg?v=6">
  <img src="assets/tiles/papertrail.svg?v=6" alt="Paper Trail — turns a reading list into a map of what rests on what." width="100%">
</picture>
</a>
</td>
<td width="50%">
<a href="https://github.com/aadycm/agent-reliability">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/tiles/agentloop.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="assets/tiles/agentloop-light.svg?v=6">
  <img src="assets/tiles/agentloop.svg?v=6" alt="Agent Reliability — 100 percent at baseline, 38 percent once search degrades." width="100%">
</picture>
</a>
</td>
</tr>
</table>

<img src="assets/divider.svg?v=6" alt="" width="100%">

### HydroNode &nbsp;·&nbsp; [hydronode.in](https://hydronode.in)

**Five growing systems on one live dashboard, each running its own controller.**

<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/projects/hydronode.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="assets/projects/hydronode-light.svg?v=6">
  <img src="assets/projects/hydronode.svg?v=6" alt="HydroNode architecture: five growing nodes and a camera feed a live path, a history path and an on-device vision path, all converging on one dashboard." width="100%">
</picture>
</p>

NFT hydroponics, a drip-irrigated terrace, a zoned sprinkler farm, aeroponic roses, and a
saffron chamber with its own climate control. Every one of them runs its watering and safety
logic **on the board**, not in the cloud — most cloud-connected garden projects stop watering
when the WiFi drops, and that seemed like the wrong way round. Each node streams live readings
to Firebase while posting a periodic row to its own Apps Script backend, so a real-time view and
a rolling 30-day history come off the same device without either path breaking the other.

The parts I'm most pleased with are about failure. History rows buffer on-device when WiFi drops
and replay later with their original timestamps. Every reboot texts me its reset cause, boot
counter and lowest free memory — that is how I found a random-reboot bug without tethering a
laptop to it. A hardware watchdog and a max-run cap keep the pump off after any hang. A camera
on the rig now classifies frames on-device for leaf stress and bloom stage; only the label ever
leaves the property, never the image.

`C++ (Arduino)` · `ESP32 / Renesas RA4M1` · `Firebase RTDB` · `Google Apps Script` · `RS485 Modbus` · `Vanilla JS PWA` · `Vercel`

<sub>~4,500 lines of firmware · ~1,900 lines of frontend · no framework, no build step · private repository</sub>

<img src="assets/divider.svg?v=6" alt="" width="100%">

### Semantic Notes

**Ask your own notes a question instead of guessing which word you used.**

<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/projects/semantic.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="assets/projects/semantic-light.svg?v=6">
  <img src="assets/projects/semantic.svg?v=6" alt="Semantic Notes: a question is embedded and matched against note vectors held on the device, then answered locally, with recall at one measured at 85.7 percent for the no-dependency version and 88.6 percent for the encoder." width="100%">
</picture>
</p>

Two versions of the same search sit in one repo so they can be compared. The first builds its
own vectors out of hashes and word co-occurrence, so it needs nothing but the standard library
— no model to download and no network call anywhere in it. The second loads a real sentence
encoder behind FastAPI and does the same job the expensive way.

Both exist because of the benchmark. 35 questions, each tagged with the note that should come
back first, all written before either version was run against them. The encoder finished **one
question ahead** — 88.6% against 85.7% recall@1 — and both put the right note in the top three
every single time. On 26 notes they are level and the gigabyte of dependencies has not paid for
itself yet. The keyword questions went to the version with no dependencies, which figures:
matching a literal token is what a posting list is for and what a dense vector blurs.

Keeping the cheap version was the useful outcome. The place an encoder should pull ahead is the
place the corpus cannot test yet — questions phrased in words the notes have never used.

`Python` · `SQLite` · `FastAPI` · `sentence-transformers` · stdlib-only core

[Repository](https://github.com/aadycm/semantic-notes)

<img src="assets/divider.svg?v=6" alt="" width="100%">

### Paper Trail

**Turns a reading list of ML papers into a map of what actually depends on what.**

<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/projects/papertrail.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="assets/projects/papertrail-light.svg?v=6">
  <img src="assets/projects/papertrail.svg?v=6" alt="Paper Trail: papers become a graph of claims and citations, highlighting which results others depend on." width="100%">
</picture>
</p>

Pulls each paper's claims and citations and graphs which results rest on which — so you can see
the one finding everything else is leaning on.

`Python` · standard library only

[Repository](https://github.com/aadycm/paper-trail)

<img src="assets/divider.svg?v=6" alt="" width="100%">

### Agent Reliability

**A tool-using LLM agent, plus a framework for finding out where it actually breaks.**

<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/projects/agentloop.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="assets/projects/agentloop-light.svg?v=6">
  <img src="assets/projects/agentloop.svg?v=6" alt="An agent loop between a model and its tools, run under three stress conditions, with success falling from 100 percent at baseline to 38 percent once search results are degraded." width="100%">
</picture>
</p>

<br>

A 23-task benchmark with known answers, a failure taxonomy, and two ablatable interventions
(reflection and self-check). No training and no GPU — it runs on a laptop against an API key.

The first study found nothing, and that is the point: the model solved every task in every
condition, so the interventions had no room to help. Self-check cost 1.4× the tokens and changed
no answer. Reflection cost 2.2× and made tool use *worse* — planning before seeing any output,
the model wrote code the sandbox blocks. Writing up a ceiling effect honestly was more useful
than quietly rewriting the tasks until something moved.

So the second study left the tasks alone and degraded the **environment** instead, which is
objective and reproducible. That found the real result: **bad information breaks an agent far
harder than broken tools do.** It retried through 42 injected tool failures and lost 2 tasks.
Truncating search results cost it 13 — and 0 of the 4 hard tasks survived. The dominant failure
was asking the same question reworded eight or nine times, getting the identical snippet back,
and running out of steps. It never once said it could not find the answer.

Two of my own heuristics turned out to be wrong, and the traces proved it: "step limit reached"
was being labelled a bad plan when the agent had already gathered every fact it needed, and the
loop detector only caught *identical* repeated calls, so every reworded loop slipped past it.

`Python` · `Gemini API` · `function calling` · `pytest`

[Repository](https://github.com/aadycm/agent-reliability)

<img src="assets/divider.svg?v=6" alt="" width="100%">

## Activity

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://streak-stats.demolab.com?user=aadycm&hide_border=true&background=15120E&stroke=3A332A&ring=E8744A&fire=E8744A&currStreakNum=F5F0E6&sideNums=F5F0E6&currStreakLabel=B2A997&sideLabels=B2A997&dates=948B7C&excludeDaysLabel=948B7C">
  <source media="(prefers-color-scheme: light)" srcset="https://streak-stats.demolab.com?user=aadycm&hide_border=true&background=F3EEE4&stroke=CDC2AD&ring=B23E08&fire=B23E08&currStreakNum=15120E&sideNums=15120E&currStreakLabel=51493C&sideLabels=51493C&dates=6B6355&excludeDaysLabel=6B6355">
  <img alt="Total contributions, current streak and longest streak" width="88%"
    src="https://streak-stats.demolab.com?user=aadycm&hide_border=true&background=15120E&stroke=3A332A&ring=E8744A&fire=E8744A&currStreakNum=F5F0E6&sideNums=F5F0E6&currStreakLabel=B2A997&sideLabels=B2A997&dates=948B7C&excludeDaysLabel=948B7C">
</picture>

</div>

<img src="assets/divider.svg?v=6" alt="" width="100%">

## How I Work

<table>
<tr>
<td width="33.3%">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/tiles/principle-1.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="assets/tiles/principle-1-light.svg?v=6">
  <img src="assets/tiles/principle-1.svg?v=6" alt="Delete before adding — the best version of most code is less of it." width="100%">
</picture>
</td>
<td width="33.3%">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/tiles/principle-2.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="assets/tiles/principle-2-light.svg?v=6">
  <img src="assets/tiles/principle-2.svg?v=6" alt="Ship it to someone — nothing is finished until someone else has used it." width="100%">
</picture>
</td>
<td width="33.3%">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/tiles/principle-3.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="assets/tiles/principle-3-light.svg?v=6">
  <img src="assets/tiles/principle-3.svg?v=6" alt="Assume it hangs — anything that can hang will, usually at 3am." width="100%">
</picture>
</td>
</tr>
</table>

<img src="assets/divider.svg?v=6" alt="" width="100%">

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/cta.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="assets/cta-light.svg?v=6">
  <img src="assets/cta.svg?v=6" alt="Have an interesting problem? Let's talk." width="100%">
</picture>

<br>

### [aadycm05@gmail.com](mailto:aadycm05@gmail.com) &nbsp;·&nbsp; [github.com/aadycm](https://github.com/aadycm) &nbsp;·&nbsp; [hydronode.in](https://hydronode.in)

</div>
