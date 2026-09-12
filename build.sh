#!/bin/sh
# Rebuilds every SVG in assets/ from the templates in src/ plus the stack lists below.
#
#   sh build.sh
#
# Each asset is generated twice — dark and light — from one source, so the two
# variants can never drift apart. Edit src/*.svg for copy, the STACK section
# here for technologies, and the palettes below for colour.

set -e
mkdir -p assets/projects

# ─────────────────────────────────────────────  palettes
#
# Contrast against the background (WCAG AA needs 4.5:1 for body text, 3:1 for large):
#   dark  --nameA 16.9  --text 13.0  --muted 8.0  --dim 5.9  --label 5.9
#   light --nameA 19.4  --text 11.3  --muted 7.4  --dim 5.9  --label 5.9
# --sep is decorative punctuation only and is deliberately below that floor.

DARK=':root{
  --bg:#0D1117; --border:#30363D;
  --v:#8B5CF6; --c:#22D3EE; --live:#34D399; --washA:.13;
  --nameA:#F4F5F8; --text:#D7DAE1; --muted:#A8AEBB; --dim:#8F96A4;
  --sheenC:#FFFFFF; --sheenA:.75; --washB:.10; --pillLit:#4A5568;
  --gridC:#FFFFFF; --gridA:.022;
  --label:#8F96A4; --sep:#41454F; --chipStroke:#363C45;
  --panel:#11161D; --wire:#3A4250; --dotOff:#3A4250; --paper:#5A6472; --track:#20262F;
}'

LIGHT=':root{
  --bg:#FFFFFF; --border:#D1D9E0;
  --v:#7C3AED; --c:#0E7490; --live:#059669; --washA:.05;
  --nameA:#0D0E11; --text:#33373F; --muted:#565C68; --dim:#666C79;
  --sheenC:#A78BFA; --sheenA:.55; --washB:.05; --pillLit:#A78BFA;
  --gridC:#0D1117; --gridA:.04;
  --label:#666C79; --sep:#C6CAD2; --chipStroke:#D8DCE2;
  --panel:#F8FAFC; --wire:#C3C9D4; --dotOff:#C3C9D4; --paper:#9AA2B0; --track:#EDEFF3;
}'

theme() { # theme <src> <out> <vars>
  awk -v vars="$3" '{ if ($0 ~ /__VARS__/) print vars; else print }' "$1" > "$2"
}

# ─────────────────────────────────────────────  hero typewriter
# PHRASES — the looping line under your name. Add or remove entries freely;
# the timing, character counts and caret travel are all computed from them.
# Keep each one under ~60 characters so it fits the hero width.

PHRASE_1="CS senior at Penn State, building AI systems."
PHRASE_2="I turn research ideas into things that run."
PHRASE_3="Currently building HydroNode."

TYPE_MS=2200      # time to type a phrase out
HOLD_MS=3000      # time it stays fully typed
DEL_MS=1300       # time to delete it
PAUSE_MS=700      # blank pause before the next one

CHAR_W=13         # px per character at font-size 25 — used for caret travel
TEXT_X=72; TEXT_Y=196; CLIP_Y=172; CARET_Y=176

build_typing() {
  n=0
  for ph in "$PHRASE_1" "$PHRASE_2" "$PHRASE_3"; do
    [ -n "$ph" ] && n=$(( n + 1 ))
  done
  SLOT_MS=$(( TYPE_MS + HOLD_MS + DEL_MS + PAUSE_MS ))
  CYCLE_MS=$(( SLOT_MS * n ))

  pct() { awk -v x="$1" -v c="$CYCLE_MS" 'BEGIN{printf "%.3f", 100*x/c}'; }

  : > .typecss.tmp
  : > .typesvg.tmp

  i=0
  for ph in "$PHRASE_1" "$PHRASE_2" "$PHRASE_3"; do
    [ -z "$ph" ] && continue
    chars=$(printf '%s' "$ph" | wc -c)
    travel=$(( chars * CHAR_W ))
    a=$(( i * SLOT_MS ))
    b=$(( a + TYPE_MS ))
    c=$(( b + HOLD_MS ))
    d=$(( c + DEL_MS ))
    pa=$(pct $a); pb=$(pct $b); pc=$(pct $c); pd=$(pct $d); pd2=$(pct $(( d + 40 )) )

    # clip-reveal keyframes
    {
      printf '    @keyframes type%s{' "$i"
      if [ "$a" -eq 0 ]; then
        printf '0%%{transform:scaleX(0);animation-timing-function:steps(%s,end)}' "$chars"
      else
        printf '0%%{transform:scaleX(0)}'
        printf '%s%%{transform:scaleX(0);animation-timing-function:steps(%s,end)}' "$pa" "$chars"
      fi
      printf '%s%%{transform:scaleX(1);animation-timing-function:linear}' "$pb"
      printf '%s%%{transform:scaleX(1);animation-timing-function:steps(%s,end)}' "$pc" "$chars"
      printf '%s%%{transform:scaleX(0)}100%%{transform:scaleX(0)}}\n' "$pd"

      # caret keyframes — travels with the text, hidden outside its slot.
      # The keyframe at pa0 holds opacity at 0 right up to the slot: without it
      # the caret fades in linearly from 0%, leaving a ghost cursor blinking at
      # the start of the line for the whole time another phrase is on screen.
      printf '    @keyframes caret%s{' "$i"
      if [ "$a" -eq 0 ]; then
        printf '0%%{opacity:1;transform:translateX(0);animation-timing-function:steps(%s,end)}' "$chars"
      else
        pa0=$(pct $(( a - 40 )) )
        printf '0%%{opacity:0;transform:translateX(0)}'
        printf '%s%%{opacity:0;transform:translateX(0)}' "$pa0"
        printf '%s%%{opacity:1;transform:translateX(0);animation-timing-function:steps(%s,end)}' "$pa" "$chars"
      fi
      printf '%s%%{opacity:1;transform:translateX(%spx);animation-timing-function:linear}' "$pb" "$travel"
      printf '%s%%{opacity:1;transform:translateX(%spx);animation-timing-function:steps(%s,end)}' "$pc" "$travel" "$chars"
      printf '%s%%{opacity:1;transform:translateX(0)}' "$pd"
      printf '%s%%{opacity:0;transform:translateX(0)}100%%{opacity:0}}\n' "$pd2"

      printf '    .t%s{animation:type%s %sms linear infinite}\n' "$i" "$i" "$CYCLE_MS"
      printf '    .c%s{animation:caret%s %sms linear infinite}\n' "$i" "$i" "$CYCLE_MS"
      # fallback when CSS animation never runs: only the first phrase shows
      if [ "$i" -gt 0 ]; then
        printf '    .t%s{transform:scaleX(0)}\n    .c%s{opacity:0}\n' "$i" "$i"
      fi
    } >> .typecss.tmp

    {
      printf '  <clipPath id="tc%s"><rect class="t t%s" x="%s" y="%s" width="%s" height="34"/></clipPath>\n' \
        "$i" "$i" "$TEXT_X" "$CLIP_Y" "$(( travel + 12 ))"
      [ "$i" -gt 0 ] && printf '  <g class="tHide">\n'
      printf '  <g clip-path="url(#tc%s)"><text class="f" x="%s" y="%s" font-size="25" font-weight="450" letter-spacing="-.3" fill="var(--text)">%s</text></g>\n' \
        "$i" "$TEXT_X" "$TEXT_Y" "$ph"
      printf '  <g class="cw c%s"><rect class="blink" x="%s" y="%s" width="2" height="26" fill="var(--c)"/></g>\n' \
        "$i" "$(( TEXT_X + 2 ))" "$CARET_Y"
      [ "$i" -gt 0 ] && printf '  </g>\n'
    } >> .typesvg.tmp

    i=$(( i + 1 ))
  done
}

build_typing

hero() { # hero <out> <vars>
  awk -v vars="$2" -v cssf=".typecss.tmp" -v svgf=".typesvg.tmp" '
    /__VARS__/     { print vars; next }
    /__TYPE_CSS__/ { while ((getline l < cssf) > 0) print l; close(cssf); next }
    /__TYPING__/   { while ((getline l < svgf) > 0) print l; close(svgf); next }
    { print }
  ' src/hero.svg > "$1"
}

hero assets/hero.svg       "$DARK"
hero assets/hero-light.svg "$LIGHT"
rm -f .typecss.tmp .typesvg.tmp

theme src/cta.svg assets/cta.svg       "$DARK"
theme src/cta.svg assets/cta-light.svg "$LIGHT"

# ─────────────────────────────────────────────  project cards
# One bespoke animated diagram per project: src/card-<name>.svg

for card in src/card-*.svg; do
  name=$(basename "$card" .svg | sed 's/^card-//')
  theme "$card" "assets/projects/$name.svg"       "$DARK"
  theme "$card" "assets/projects/$name-light.svg" "$LIGHT"
done

for panel in src/panel-*.svg; do
  name=$(basename "$panel" .svg | sed 's/^panel-//')
  theme "$panel" "assets/$name.svg"       "$DARK"
  theme "$panel" "assets/$name-light.svg" "$LIGHT"
done

# ─────────────────────────────────────────────  divider

cat > assets/divider.svg <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 12" width="1280" height="12" role="img" aria-label="">
  <defs>
    <style>
      @keyframes glide{0%{transform:translateX(-200px)}100%{transform:translateX(1320px)}}
      @keyframes fade{0%,100%{opacity:0}15%,85%{opacity:.9}}
      @keyframes glideBack{0%{transform:translateX(1320px)}100%{transform:translateX(-200px)}}
      @keyframes fade2{0%,100%{opacity:0}20%,80%{opacity:.45}}
      @keyframes nodePulse{0%,100%{opacity:.35;transform:scale(1)}50%{opacity:1;transform:scale(1.5)}}
      .trav{animation:glide 11s cubic-bezier(.4,0,.6,1) infinite,fade 11s linear infinite}
      .trav2{animation:glideBack 17s cubic-bezier(.4,0,.6,1) 5s infinite,fade2 17s linear 5s infinite}
      .node{transform-box:fill-box;transform-origin:center;animation:nodePulse 5s ease-in-out infinite}
      @media (prefers-reduced-motion:reduce){
        .trav,.trav2,.node{animation:none}
        .trav,.trav2{opacity:0}
      }
    </style>
    <linearGradient id="d" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#8B5CF6" stop-opacity="0"/>
      <stop offset="50%" stop-color="#8B5CF6" stop-opacity=".38"/>
      <stop offset="100%" stop-color="#8B5CF6" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="t" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#22D3EE" stop-opacity="0"/>
      <stop offset="50%" stop-color="#67E8F9" stop-opacity="1"/>
      <stop offset="100%" stop-color="#22D3EE" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x="0" y="5.5" width="1280" height="1" fill="url(#d)"/>
  <rect class="trav2" x="0" y="5" width="150" height="2" rx="1" fill="url(#t)"/>
  <rect class="trav" x="0" y="5" width="200" height="2" rx="1" fill="url(#t)"/>
  <circle class="node" cx="640" cy="6" r="2" fill="#8B5CF6"/>
</svg>
EOF

# ─────────────────────────────────────────────  project placeholder

cat > assets/projects/placeholder.svg <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630" role="img" aria-label="Project screenshot placeholder">
  <defs><style>.m{font-family:'SF Mono','JetBrains Mono',ui-monospace,Menlo,Consolas,monospace}</style></defs>
  <rect width="1200" height="630" rx="14" fill="#0D1117"/>
  <rect x=".75" y=".75" width="1198.5" height="628.5" rx="14" fill="none" stroke="#30363D" stroke-width="1.5"/>
  <g transform="translate(600,300)" fill="none" stroke="#5B5F6B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="-34" y="-26" width="68" height="52" rx="6"/>
    <path d="M-34 12 L-12 -8 L4 8 L16 -2 L34 12"/>
    <circle cx="14" cy="-12" r="4.5"/>
  </g>
  <text class="m" x="600" y="376" text-anchor="middle" font-size="15" letter-spacing="1.8" fill="#71767F">SCREENSHOT 1200 x 630</text>
</svg>
EOF


# ─────────────────────────────────────────────  tech stack
# STACK — edit these six lines. Underscores become spaces.

L_LANGUAGES="Python TypeScript Java C SQL"
L_FRONTEND="React Next.js Tailwind_CSS"
L_BACKEND="FastAPI Node.js Flask REST_APIs"
L_DATA="PostgreSQL MongoDB Redis Pinecone"
L_CLOUD="AWS Docker Git GitHub_Actions Linux"
L_TOOLING="PyTorch Hugging_Face LangChain scikit-learn OpenCV"

LABEL_X=72; CHIP_X=248; RIGHT=1208; ROW_GAP=34; TOTAL_ROWS=6

# scan band: sweeps the panel, and each chip lights up as it passes
SCAN_CYCLE_MS=14000
SCAN_DELAY_MS=2000
SCAN_MOVE_MS=7700
SCAN_MOVE_PCT=$(( SCAN_MOVE_MS * 100 / SCAN_CYCLE_MS ))
y=52; row=0
: > .rows.tmp

emit_row() { # emit_row <label> <items...>
  label=$1; shift
  delay=$(( row * 90 ))
  {
    printf '  <g transform="translate(0,%s)"><g class="in" style="animation-delay:%sms">\n' "$y" "$delay"
    printf '    <text class="m" x="%s" y="20" font-size="11.5" letter-spacing="1.6" fill="var(--label)">%s</text>\n' "$LABEL_X" "$label"
  } >> .rows.tmp

  cx=$CHIP_X; cy=0; n=0; lines=1
  for item in "$@"; do
    name=$(echo "$item" | tr '_' ' ')
    len=$(printf '%s' "$name" | wc -c)
    w=$(( len * 7 + 26 ))
    if [ $(( cx + w )) -gt $RIGHT ]; then cx=$CHIP_X; cy=$(( cy + 38 )); lines=$(( lines + 1 )); fi
    cd_=$(( delay + 120 + n * 40 ))
    half=$(( w / 2 ))
    # the scan band sweeps 1700px over SCAN_MOVE_MS starting at SCAN_DELAY_MS;
    # time the chip's glow to the moment the band's centre crosses it
    chipMid=$(( cx + half ))
    glow=$(( SCAN_DELAY_MS + SCAN_MOVE_MS * (chipMid + 190) / 1700 - 250 ))
    [ "$glow" -lt 0 ] && glow=0
    printf '    <g transform="translate(%s,%s)"><g class="chip" style="animation-delay:%sms"><rect class="chipR" style="animation-delay:%sms" width="%s" height="28" rx="14" fill="none" stroke="var(--chipStroke)"/><text class="f" x="%s" text-anchor="middle" y="19" font-size="12.5" font-weight="450" fill="var(--text)">%s</text></g></g>\n' "$cx" "$cy" "$cd_" "$glow" "$w" "$half" "$name" >> .rows.tmp
    cx=$(( cx + w + 8 )); n=$(( n + 1 ))
  done

  rowH=$(( lines * 28 + (lines - 1) * 10 ))
  y=$(( y + rowH + ROW_GAP ))
  row=$(( row + 1 ))
  if [ $row -lt $TOTAL_ROWS ]; then
    printf '    <rect class="hair" style="animation-delay:%sms" x="%s" y="%s" width="%s" height="1" fill="var(--border)"/>\n' \
      "$(( delay + 240 ))" "$LABEL_X" "$(( rowH + 16 ))" "$(( RIGHT - LABEL_X ))" >> .rows.tmp
  fi
  printf '  </g></g>\n' >> .rows.tmp
}

emit_row "LANGUAGES"   $L_LANGUAGES
emit_row "AI / ML"     $L_TOOLING
emit_row "BACKEND"     $L_BACKEND
emit_row "FRONTEND"    $L_FRONTEND
emit_row "DATA"        $L_DATA
emit_row "INFRA / OPS" $L_CLOUD

H=$(( y - ROW_GAP + 44 ))

{
cat <<HDR
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 $H" width="1280" height="$H" role="img" aria-label="Tech stack by category">
  <defs>
    <style>
__VARS__
      .f{font-family:'Inter','SF Pro Display',-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif}
      .m{font-family:'SF Mono','JetBrains Mono',ui-monospace,Menlo,Consolas,monospace}
      @keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
      @keyframes pop{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}
      @keyframes scan{0%{transform:translateX(0)}${SCAN_MOVE_PCT}%,100%{transform:translateX(1700px)}}
      @keyframes chipGlow{0%,100%{stroke:var(--chipStroke)}2%{stroke:var(--v)}3%{stroke:var(--v)}7%{stroke:var(--chipStroke)}}
      @keyframes drawLine{from{transform:scaleX(0)}to{transform:scaleX(1)}}
      .in{animation:rise .7s cubic-bezier(.16,.84,.24,1) backwards}
      .chip{animation:pop .5s cubic-bezier(.16,.84,.24,1) backwards}
      .chipR{animation:chipGlow ${SCAN_CYCLE_MS}ms linear infinite}
      .hair{transform-box:fill-box;transform-origin:left center;
        animation:drawLine .9s cubic-bezier(.16,.84,.24,1) backwards}
      .scan{animation:scan ${SCAN_CYCLE_MS}ms linear ${SCAN_DELAY_MS}ms infinite}
      @media (prefers-reduced-motion:reduce){
        .in,.chip,.chipR,.hair,.scan{animation:none!important}
        .scan{display:none}
        .hair{transform:none}
      }
    </style>
    <linearGradient id="scanG" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="var(--v)" stop-opacity="0"/>
      <stop offset="50%" stop-color="var(--v)" stop-opacity=".10"/>
      <stop offset="100%" stop-color="var(--v)" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="panelClip"><rect x=".75" y=".75" width="1278.5" height="$(( H - 2 ))" rx="16"/></clipPath>
  </defs>
  <rect width="1280" height="$H" fill="var(--bg)"/>
  <rect x=".75" y=".75" width="1278.5" height="$(( H - 2 )).5" rx="16" fill="none" stroke="var(--border)" stroke-width="1.5"/>
HDR
cat .rows.tmp
printf '  <g clip-path="url(#panelClip)"><rect class="scan" x="-320" y="0" width="260" height="%s" fill="url(#scanG)"/></g>\n' "$H"
printf '</svg>\n'
} > .stack.tmp

theme .stack.tmp assets/stack.svg       "$DARK"
theme .stack.tmp assets/stack-light.svg "$LIGHT"
rm -f .stack.tmp .rows.tmp

echo "built (stack height ${H}px): $(ls assets/*.svg | tr '\n' ' ')"
