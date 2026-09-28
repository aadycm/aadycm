<!-- ────────────────────────────────────────────────────────────────
     Rebuild the SVGs after any edit:  sh build.sh
     Setup + checklist: SETUP.md
     ──────────────────────────────────────────────────────────── -->

<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero.svg?v=3">
  <source media="(prefers-color-scheme: light)" srcset="assets/hero-light.svg?v=3">
  <img src="assets/hero.svg?v=3" alt="Aadithya Chandramouli — CS senior at Penn State, building AI systems." width="100%">
</picture>
</p>

<img src="assets/divider.svg?v=3" alt="" width="100%">

## About

I'm a computer science senior at Penn State. Most of what I build ends up being machine
learning plus everything around it — the sensors, the pipeline, the API, the dashboard someone
actually opens. The model is usually the part that takes the least time.

- Most of my projects started because something annoyed me. HydroNode exists because I got
  tired of plants dying while I was away.
- I'd rather have something rough running this week than something perfect next month. The
  rough version is what tells you which half of the plan was wrong.
- I've spent enough nights chasing a crash that turned out to be a loose wire to care a lot
  about logs, watchdogs, and things that fail loudly.

<table>
<tr>
<td width="50%" valign="top">

**Right now** — teaching HydroNode to look at the plants instead of just measuring the air.

</td>
<td width="50%" valign="top">

**Figuring out** — how small a model can get before it stops being useful on a board with no GPU.

</td>
</tr>
</table>

<img src="assets/divider.svg?v=3" alt="" width="100%">

## Stack

<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/stack.svg?v=3">
  <source media="(prefers-color-scheme: light)" srcset="assets/stack-light.svg?v=3">
  <img src="assets/stack.svg?v=3" alt="Stack — languages, AI and ML, backend, frontend, data, infrastructure" width="100%">
</picture>
</p>

<img src="assets/divider.svg?v=3" alt="" width="100%">

## Selected Work

### HydroNode &nbsp;·&nbsp; [hydronode.in](https://hydronode.in)

**Five growing systems on one live dashboard, each running its own controller.**

<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/projects/hydronode.svg?v=3">
  <source media="(prefers-color-scheme: light)" srcset="assets/projects/hydronode-light.svg?v=3">
  <img src="assets/projects/hydronode.svg?v=3" alt="HydroNode architecture: five growing nodes and a camera feed a live path, a history path and an on-device vision path, all converging on one dashboard." width="100%">
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

<img src="assets/divider.svg?v=3" alt="" width="100%">

### Semantic Notes

**Ask your own notes a question instead of guessing which word you used.**

<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/projects/semantic.svg?v=3">
  <source media="(prefers-color-scheme: light)" srcset="assets/projects/semantic-light.svg?v=3">
  <img src="assets/projects/semantic.svg?v=3" alt="Semantic Notes: a question is embedded and matched against note vectors held on the device, then answered locally." width="100%">
</picture>
</p>

Everything is embedded and searched on the machine, so no notes leave it and there's no network
round-trip in the loop.

`Python` · `SQLite` · standard library only

[Repository](https://github.com/aadycm/semantic-notes)

<img src="assets/divider.svg?v=3" alt="" width="100%">

### Paper Trail

**Turns a reading list of ML papers into a map of what actually depends on what.**

<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/projects/papertrail.svg?v=3">
  <source media="(prefers-color-scheme: light)" srcset="assets/projects/papertrail-light.svg?v=3">
  <img src="assets/projects/papertrail.svg?v=3" alt="Paper Trail: papers become a graph of claims and citations, highlighting which results others depend on." width="100%">
</picture>
</p>

Pulls each paper's claims and citations and graphs which results rest on which — so you can see
the one finding everything else is leaning on.

`Python` · standard library only

[Repository](https://github.com/aadycm/paper-trail)

<img src="assets/divider.svg?v=3" alt="" width="100%">

### Agent Reliability

**A tool-using LLM agent, plus a framework for finding out where it actually breaks.**

<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/projects/agentloop.svg?v=3">
  <source media="(prefers-color-scheme: light)" srcset="assets/projects/agentloop-light.svg?v=3">
  <img src="assets/projects/agentloop.svg?v=3" alt="An agent loop between a model and its tools, run under three stress conditions, with success falling from 100 percent at baseline to 38 percent once search results are degraded." width="100%">
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

<img src="assets/divider.svg?v=3" alt="" width="100%">

## Activity

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://streak-stats.demolab.com?user=aadycm&hide_border=true&background=0D1117&stroke=30363D&ring=8B5CF6&fire=22D3EE&currStreakNum=F4F5F8&sideNums=F4F5F8&currStreakLabel=A8AEBB&sideLabels=A8AEBB&dates=8F96A4&excludeDaysLabel=8F96A4">
  <source media="(prefers-color-scheme: light)" srcset="https://streak-stats.demolab.com?user=aadycm&hide_border=true&background=FFFFFF&stroke=D1D9E0&ring=7C3AED&fire=0E7490&currStreakNum=0D0E11&sideNums=0D0E11&currStreakLabel=565C68&sideLabels=565C68&dates=666C79&excludeDaysLabel=666C79">
  <img alt="Total contributions, current streak and longest streak" width="88%"
    src="https://streak-stats.demolab.com?user=aadycm&hide_border=true&background=0D1117&stroke=30363D&ring=8B5CF6&fire=22D3EE&currStreakNum=F4F5F8&sideNums=F4F5F8&currStreakLabel=A8AEBB&sideLabels=A8AEBB&dates=8F96A4&excludeDaysLabel=8F96A4">
</picture>

<br>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-profile-summary-cards.vercel.app/api/cards/stats?username=aadycm&theme=github_dark">
  <source media="(prefers-color-scheme: light)" srcset="https://github-profile-summary-cards.vercel.app/api/cards/stats?username=aadycm&theme=default">
  <img height="200" alt="Commits, pull requests, issues and contributions"
    src="https://github-profile-summary-cards.vercel.app/api/cards/stats?username=aadycm&theme=github_dark">
</picture>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-profile-summary-cards.vercel.app/api/cards/productive-time?username=aadycm&theme=github_dark&utcOffset=5.5">
  <source media="(prefers-color-scheme: light)" srcset="https://github-profile-summary-cards.vercel.app/api/cards/productive-time?username=aadycm&theme=default&utcOffset=5.5">
  <img height="200" alt="When during the day the commits happen"
    src="https://github-profile-summary-cards.vercel.app/api/cards/productive-time?username=aadycm&theme=github_dark&utcOffset=5.5">
</picture>

</div>

<img src="assets/divider.svg?v=3" alt="" width="100%">

## How I Work

> I'd rather delete code than add it.
>
> Nothing is finished until someone else has used it and told me what's wrong with it.
>
> Anything that can hang, will — usually at 3am, while I'm asleep.

<img src="assets/divider.svg?v=3" alt="" width="100%">

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/cta.svg?v=3">
  <source media="(prefers-color-scheme: light)" srcset="assets/cta-light.svg?v=3">
  <img src="assets/cta.svg?v=3" alt="Have an interesting problem? Let's talk." width="100%">
</picture>

<br>

### [aadycm05@gmail.com](mailto:aadycm05@gmail.com) &nbsp;·&nbsp; [github.com/aadycm](https://github.com/aadycm) &nbsp;·&nbsp; [hydronode.in](https://hydronode.in)

</div>
