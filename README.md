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

I'm a computer science senior at Penn State who spends most of his time on **machine learning
and the systems around it** — the data pipeline, the API, the thing that has to keep running
when the network doesn't. The model is usually the easy part.

- **I like problems where the data is messy.** Clean benchmarks don't teach you much.
- **Ship it, then judge it.** A rough version in someone's hands beats a perfect notebook.
- **Assume it will fail.** Watchdogs, fallbacks, and honest logs beat clever code that only works.

<table>
<tr>
<td width="50%" valign="top">

**Building** — HydroNode, plus two AI projects in early stages.

</td>
<td width="50%" valign="top">

**Learning** — retrieval-augmented generation, model evaluation, and how to make inference cheap.

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

**A self-built IoT platform running two growing systems — NFT hydroponics and a drip-irrigated
terrace garden — on one live dashboard.**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/projects/hydronode.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/projects/hydronode-light.svg">
  <img src="assets/projects/hydronode.svg" alt="HydroNode two-path architecture: growing nodes stream live readings to Firebase and post a periodic history to Google Sheets, both feeding one dashboard." width="100%">
</picture>

Most cloud-connected garden projects stop watering when the WiFi drops. HydroNode inverts that:
**every watering and safety decision runs on the microcontroller**, and the network exists only
for reporting and remote control. Two boards — an Arduino Nano ESP32 and an Uno R4 WiFi — each
push live readings into Firebase Realtime Database while posting a periodic row to their own
Google Apps Script backend, giving a real-time view and a rolling 30-day history from the same
device without either path being able to break the other.

The engineering I'm proudest of is the failure handling:

- **Offline spool** — when WiFi drops, history rows buffer on-device and replay later with their
  original timestamps, so an outage leaves no gap in the analytics.
- **Self-diagnosing reboots** — the board pushes its reset cause, boot counter, and lowest free
  memory to my phone on every restart. That's how I tracked down a real random-reboot bug
  without ever tethering a laptop to it.
- **Fail-safe actuation** — hardware watchdog, pump guaranteed OFF on boot and after any hang,
  and a max-run cap that force-stops a cycle that overruns.
- **Heartbeat liveness** — the dashboard marks a node dead 90 seconds after its heartbeat stops,
  which is a different question from whether the readings changed.
- **Sensor beats forecast** — dual debounced rain sensors cancel a scheduled watering, and the
  device's own reading overrides the weather API.

On top of that: VPD computed on-device rather than raw temperature and humidity, a calendar
heat-map of how well conditions held in band, per-user database rules so only a garden's owner
can touch its controls, and a monthly rollover that keeps the history sheet fast.

`C++ (Arduino)` · `ESP32 / Renesas RA4M1` · `Firebase RTDB` · `Google Apps Script` · `RS485 Modbus` · `Vanilla JS PWA` · `Vercel`

<sub>~4,500 lines of firmware · ~1,900 lines of frontend · no framework, no build step · private repository</sub>

<img src="assets/divider.svg" alt="" width="100%">

### Semantic Notes

**A local-first note app that answers questions about your own notes.**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/projects/semantic.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/projects/semantic-light.svg">
  <img src="assets/projects/semantic.svg" alt="Semantic Notes: a question is embedded and matched against note vectors held on the device, then answered locally." width="100%">
</picture>

Keyword search fails exactly when you need it — when you can't remember the words you used.
This embeds every note on the device and answers plain questions against them, so nothing is
uploaded and there's no cloud round-trip in the loop.

`Python` · `FastAPI` · `Sentence Transformers` · `SQLite`

<sub>In progress</sub>

### Paper Trail

**Turns a reading list of ML papers into a map of what actually depends on what.**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/projects/papertrail.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/projects/papertrail-light.svg">
  <img src="assets/projects/papertrail.svg" alt="Paper Trail: papers become a graph of claims and citations, highlighting which results others depend on." width="100%">
</picture>

Reading fifty papers leaves you with fifty summaries and no structure. This extracts each
paper's claims and citations and builds a graph of which results rest on which — so a line of
work shows you where it actually holds up, and which single result everything else is leaning on.

`Python` · `PyTorch` · `React` · `Neo4j`

<sub>In progress</sub>

<img src="assets/divider.svg" alt="" width="100%">

## Activity

<div align="center">

<a href="https://github.com/aadycm">
  <img height="150" alt="GitHub statistics"
    src="https://github-readme-stats.vercel.app/api?username=aadycm&show_icons=true&count_private=true&include_all_commits=true&hide_border=true&hide_title=true&bg_color=0D1117&text_color=A8AEBB&icon_color=8B5CF6&ring_color=8B5CF6">
</a>
<a href="https://github.com/aadycm">
  <img height="150" alt="Most used languages"
    src="https://github-readme-stats.vercel.app/api/top-langs/?username=aadycm&layout=compact&langs_count=6&hide_border=true&hide_title=true&bg_color=0D1117&text_color=A8AEBB">
</a>

</div>

## How I Work

> **Simple beats clever.** The best PR is usually the one that deletes code.
>
> **Ship to learn.** Real users find the flaws a spec never will.
>
> **Design for the failure.** Anything that can hang, will — at 3am, while you're asleep.

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
