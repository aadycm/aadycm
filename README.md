<!-- ────────────────────────────────────────────────────────────────
     Rebuild the SVGs after any edit:  sh build.sh
     Setup + checklist: SETUP.md
     ──────────────────────────────────────────────────────────── -->

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/hero-light.svg">
  <img src="assets/hero.svg" alt="Aadithya Chandramouli — CS senior at Penn State, building AI systems." width="100%">
</picture>

</div>

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

<img src="assets/divider.svg" alt="" width="100%">

## Stack

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/stack.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/stack-light.svg">
  <img src="assets/stack.svg" alt="Stack — languages, AI and ML, backend, frontend, data, infrastructure" width="100%">
</picture>

## Selected Work

### HydroNode &nbsp;·&nbsp; [hydronode.in](https://hydronode.in)

**Five growing systems on one live dashboard, each running its own controller.**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/projects/hydronode.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/projects/hydronode-light.svg">
  <img src="assets/projects/hydronode.svg" alt="HydroNode architecture: five growing nodes and a camera feed a live path, a history path and an on-device vision path, all converging on one dashboard." width="100%">
</picture>

NFT hydroponics, a drip-irrigated terrace, a zoned sprinkler farm, aeroponic roses, and a
saffron chamber with its own climate control. Every one of them runs its watering and safety
logic **on the board**, not in the cloud — most cloud-connected garden projects stop watering
when the WiFi drops, and that seemed like the wrong way round.

Each node pushes live readings into Firebase Realtime Database while posting a periodic row to
its own Google Apps Script backend. That gives a real-time view and a rolling 30-day history
from the same device, without either path being able to break the other.

**Computer vision**, the part I'm working on now: a camera on the rig classifies frames
on-device rather than shipping them anywhere. It's learning to flag leaf stress and
discolouration early, tell which stage the roses are at so the misting cycle can follow the
bloom instead of a fixed clock, and spot saffron flowers opening so harvest doesn't miss the
window. Only the label leaves the property — never the image.

The parts I'm most pleased with are all about failure:

- **Offline spool** — when WiFi drops, history rows buffer on-device and replay later with their
  original timestamps, so an outage leaves no gap in the analytics.
- **Reboots that explain themselves** — the board texts my phone its reset cause, boot counter,
  and lowest free memory on every restart. That's how I found a random-reboot bug without ever
  tethering a laptop to it.
- **Fail-safe actuation** — hardware watchdog, pump guaranteed OFF on boot and after any hang,
  and a max-run cap that force-stops a cycle that overruns.
- **Heartbeat liveness** — a node is marked dead 90 seconds after its heartbeat stops, which is
  a different question from whether the readings changed.
- **Sensors beat forecasts** — dual debounced rain sensors cancel a scheduled watering, and the
  device's own reading overrides the weather API.

Plus VPD computed on-device rather than raw temperature and humidity, a calendar heat-map of how
well conditions held in band, per-user database rules so only a garden's owner can touch its
controls, and a monthly rollover that keeps the history sheet fast.

`C++ (Arduino)` · `ESP32 / Renesas RA4M1` · `Firebase RTDB` · `Google Apps Script` · `RS485 Modbus` · `Vanilla JS PWA` · `Vercel`

<sub>~4,500 lines of firmware · ~1,900 lines of frontend · no framework, no build step · private repository</sub>

<img src="assets/divider.svg" alt="" width="100%">

### Semantic Notes

**Ask your own notes a question instead of guessing which word you used.**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/projects/semantic.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/projects/semantic-light.svg">
  <img src="assets/projects/semantic.svg" alt="Semantic Notes: a question is embedded and matched against note vectors held on the device, then answered locally." width="100%">
</picture>

Everything is embedded and searched on the machine, so no notes leave it and there's no network
round-trip in the loop.

`Python` · `FastAPI` · `Sentence Transformers` · `SQLite`

<sub>In progress · private repository</sub>

### Paper Trail

**Turns a reading list of ML papers into a map of what actually depends on what.**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/projects/papertrail.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/projects/papertrail-light.svg">
  <img src="assets/projects/papertrail.svg" alt="Paper Trail: papers become a graph of claims and citations, highlighting which results others depend on." width="100%">
</picture>

Pulls each paper's claims and citations and graphs which results rest on which — so you can see
the one finding everything else is leaning on.

`Python` · `PyTorch` · `React` · `Neo4j`

<sub>In progress · private repository</sub>

<img src="assets/divider.svg" alt="" width="100%">

## Activity

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/focus.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/focus-light.svg">
  <img src="assets/focus.svg" alt="Where the work goes: embedded firmware, machine learning, backend and data, frontend, infrastructure — with a recent activity trace." width="100%">
</picture>

## How I Work

> I'd rather delete code than add it.
>
> Nothing is finished until someone else has used it and told me what's wrong with it.
>
> Anything that can hang, will — usually at 3am, while I'm asleep.

<img src="assets/divider.svg" alt="" width="100%">

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/cta.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/cta-light.svg">
  <img src="assets/cta.svg" alt="Have an interesting problem? Let's talk." width="100%">
</picture>

<br>

### [aadycm05@gmail.com](mailto:aadycm05@gmail.com) &nbsp;·&nbsp; [github.com/aadycm](https://github.com/aadycm) &nbsp;·&nbsp; [hydronode.in](https://hydronode.in)

</div>
