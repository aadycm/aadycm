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
  --netLine:#3B4658; --netDot:#6D7A8C; --netSig:#22D3EE;
  --orbInk:#E7EAF0;
}'

LIGHT=':root{
  --bg:#FFFFFF; --border:#D1D9E0;
  --v:#7C3AED; --c:#0E7490; --live:#059669; --washA:.05;
  --nameA:#0D0E11; --text:#33373F; --muted:#565C68; --dim:#666C79;
  --sheenC:#A78BFA; --sheenA:.55; --washB:.05; --pillLit:#A78BFA;
  --gridC:#0D1117; --gridA:.04;
  --label:#666C79; --sep:#C6CAD2; --chipStroke:#D8DCE2;
  --panel:#F8FAFC; --wire:#C3C9D4; --dotOff:#C3C9D4; --paper:#9AA2B0; --track:#EDEFF3;
  --netLine:#CBD2DC; --netDot:#98A1B0; --netSig:#0E7490;
  --orbInk:#12141A;
}'

theme() { # theme <src> <out> <vars>
  awk -v vars="$3" '{ if ($0 ~ /__VARS__/) print vars; else print }' "$1" > "$2"
}

# render <src> <out> <vars> — like theme(), but any __TOKEN__ line is replaced
# by the contents of .frag.TOKEN when that fragment exists (see gen_net, gen_orb).
render() {
  awk -v vars="$3" '
    /__VARS__/ { print vars; next }
    /^[ \t]*__[A-Z_]+__[ \t]*$/ {
      name=$0; sub(/^[ \t]*__/,"",name); sub(/__[ \t]*$/,"",name)
      f=".frag." name; any=0
      while ((getline l < f) > 0) { print l; any=1 }
      close(f)
      if (any) next
    }
    { print }
  ' "$1" > "$2"
}

# ─────────────────────────────────────────────  particle network
# Nodes scattered in a region, edges between any pair closer than MAXD, and a
# few signals that travel an edge end to end. Positions come from a seeded RNG
# so the layout is identical on every build.

gen_net() { # gen_net <x0> <y0> <x1> <y1> <count> <seed> <maxd> <signals> <opacity>
  awk -v X0="$1" -v Y0="$2" -v X1="$3" -v Y1="$4" -v N="$5" -v SEED="$6" \
      -v MAXD="$7" -v SIG="$8" -v OP="$9" 'BEGIN{
    srand(SEED)
    # Jittered grid, not pure random: a uniform random scatter clumps in places
    # and leaves holes elsewhere, which reads as noise rather than a network.
    W = X1-X0; H = Y1-Y0
    cols = int(sqrt(N*W/H) + 0.5); if(cols<1) cols=1
    rows = int(N/cols + 0.999); if(rows<1) rows=1
    cw = W/cols; ch = H/rows
    k=0
    for(rr=0; rr<rows; rr++) for(cc=0; cc<cols && k<N; cc++){
      x[k] = X0 + cc*cw + cw*(0.20+rand()*0.60)
      y[k] = Y0 + rr*ch + ch*(0.20+rand()*0.60)
      r[k] = 1.2+rand()*1.4; nd[k] = rand()*9; k++ }
    N = k
    # edges follow the grid pitch, so every node keeps a couple of neighbours
    if (MAXD+0 == 0) MAXD = (cw>ch?cw:ch)*1.45
    ne=0
    for(i=0;i<N;i++) for(j=i+1;j<N;j++){
      dx=x[i]-x[j]; dy=y[i]-y[j]; d=sqrt(dx*dx+dy*dy)
      if(d<MAXD){ ei[ne]=i; ej[ne]=j; ne++ } }

    SVG=".frag.NET_SVG"; CSS=".frag.NET_CSS"
    printf "" > SVG; printf "" > CSS

    print "  <g class=\"net\" opacity=\"" OP "\">" > SVG
    for(e=0;e<ne;e++)
      printf "    <line class=\"edge\" style=\"animation-delay:%.2fs\" x1=\"%.1f\" y1=\"%.1f\" x2=\"%.1f\" y2=\"%.1f\"/>\n",
             (e%11)*0.8, x[ei[e]],y[ei[e]],x[ej[e]],y[ej[e]] > SVG
    for(i=0;i<N;i++)
      printf "    <circle class=\"nd\" style=\"animation-delay:%.2fs\" cx=\"%.1f\" cy=\"%.1f\" r=\"%.2f\"/>\n",
             nd[i], x[i],y[i],r[i] > SVG

    print "    @keyframes edgeLive{0%,100%{opacity:.35}50%{opacity:1}}" > CSS
    print "    @keyframes ndLive{0%,100%{opacity:.45;r:var(--nr)}50%{opacity:1}}" > CSS
    print "    .net .edge{stroke:var(--netLine);stroke-width:1;animation:edgeLive 9s ease-in-out infinite}" > CSS
    print "    .net .nd{fill:var(--netDot);animation:ndLive 7s ease-in-out infinite}" > CSS

    # signals: spread the picks across the edge list so they do not overlap
    for(s=0; s<SIG && ne>0; s++){
      e = int(ne/SIG)*s
      dx = x[ej[e]]-x[ei[e]]; dy = y[ej[e]]-y[ei[e]]
      printf "    <circle class=\"sig g%d\" cx=\"%.1f\" cy=\"%.1f\" r=\"2.1\"/>\n", s, x[ei[e]], y[ei[e]] > SVG
      printf "    @keyframes sig%d{0%%{transform:translate(0,0);opacity:0}12%%{opacity:1}85%%{opacity:1}100%%{transform:translate(%.1fpx,%.1fpx);opacity:0}}\n",
             s, dx, dy > CSS
      printf "    .net .g%d{animation:sig%d %.1fs cubic-bezier(.45,0,.55,1) %.1fs infinite}\n",
             s, s, 3.4+s*0.9, s*1.3 > CSS
    }
    print "    .net .sig{fill:var(--netSig)}" > CSS
    print "  </g>" > SVG
    print "    @media (prefers-reduced-motion:reduce){.net .edge,.net .nd,.net .sig{animation:none!important}.net .sig{opacity:0}}" > CSS
  }'
}

# ─────────────────────────────────────────────  thinking orb
# Modelled on the "orbits" state of Jakub Antalik's thinking-orbs
# (github.com/Jakubantalik/thinking-orbs): coreless and strictly monochrome —
# tilted orbits, each a dotted ghost path with brighter particles running it.
# A tilted circle projects to an ellipse, so each orbit is generated as one,
# with the particle's path emitted as translate keyframes and its depth (size
# and opacity) as a second animation on the same clock.

gen_orb() { # gen_orb <cx> <cy> <r>
  awk -v CX="$1" -v CY="$2" -v RR="$3" '
  function acos(x){ return atan2(sqrt(1-x*x), x) }
  # awk int() truncates toward zero; JS Math.floor rounds down. Using int()
  # here silently produced a different hash for every negative value.
  function floor(x){ return (x>=0) ? int(x) : ((x==int(x)) ? x : int(x)-1) }
  function hashD(a,b,  h){ h = sin(a*12.9898 + b*78.233)*43758.5453; return h - floor(h) }
  BEGIN{
    SVG=".frag.ORB_SVG"; CSS=".frag.ORB_CSS"
    printf "" > SVG; printf "" > CSS
    PI=3.14159265358979
    R  = RR*0.82          # orbits.ts: R = (size/2)*0.82
    ORBITS=12; GHOST=30; PARTS=2; STEPS=24
    TILT=0.3              # makeProj(yaw, tilt=0.3, ...) — yaw held at 0
    SPD=1.885             # the tuned "orbits" preset speed
    rs = ((RR*2)/300)^0.6 # radiusScale(size, 0.6)
    ghostR = 0.9*rs; partR = 1.2*rs; partDepth = 1.6*rs
    ct=cos(TILT); st=sin(TILT)

    printf "  <g class=\"orb\" transform=\"translate(%s,%s)\">\n", CX, CY > SVG

    for(i=0;i<ORBITS;i++){
      h1=hashD(i,1.7); h2=hashD(i,5.2); h3=hashD(i,8.9)
      ro  = R*(0.45+0.52*h1)
      th  = h1*2*PI
      phi = acos(2*h2-1)
      nx=sin(phi)*cos(th); ny=cos(phi); nz=sin(phi)*sin(th)
      ux=-ny; uy=nx; uz=0
      ul=sqrt(ux*ux+uy*uy); if(ul<1e-6) ul=1e-6
      ux/=ul; uy/=ul
      vx = ny*uz - nz*uy
      vy = nz*ux - nx*uz
      vz = nx*uy - ny*ux
      sp  = (0.25+0.55*h3) * ((h3>0.5)?1:-1)
      ppd = (2*PI/((sp<0)?-sp:sp))/SPD      # seconds for one lap

      # ghost path — every dot at its own projected position, so it is a plain
      # round circle. No group transform, nothing to distort it.
      for(g=0; g<GHOST; g++){
        a  = (g/GHOST)*2*PI
        ca = cos(a); sa = sin(a)
        X = (ux*ca + vx*sa)*ro; Y = (uy*ca + vy*sa)*ro; Z = (uz*ca + vz*sa)*ro
        y1 = Y*ct - Z*st; z2 = Y*st + Z*ct
        depth = (z2/ro + 1)/2
        printf "    <circle class=\"gh\" cx=\"%.2f\" cy=\"%.2f\" r=\"%.2f\" opacity=\"%.3f\"/>\n",
               X, -y1, ghostR, 0.5*(0.4+0.6*depth) > SVG
      }

      # particles — one keyframe track each, carrying position, depth size and
      # depth opacity together, so they ride the real 3-D orbit
      for(m=0;m<PARTS;m++){
        ph = (m/PARTS)*2*PI + h2*6
        id = i "_" m
        printf "    @keyframes pk%s{", id > CSS
        for(s=0;s<=STEPS;s++){
          a  = ph + sp/((sp<0)?-sp:sp) * (s/STEPS)*2*PI
          ca = cos(a); sa = sin(a)
          X = (ux*ca + vx*sa)*ro; Y = (uy*ca + vy*sa)*ro; Z = (uz*ca + vz*sa)*ro
          y1 = Y*ct - Z*st; z2 = Y*st + Z*ct
          depth = (z2/ro + 1)/2
          printf "%.2f%%{transform:translate(%.2fpx,%.2fpx) scale(%.3f);opacity:%.3f}",
                 (s/STEPS)*100, X, -y1, (partR+partDepth*depth)/partR, 0.45+0.5*depth > CSS
        }
        print "}" > CSS
        printf "    .pk%s{animation:pk%s %.2fs linear infinite}\n", id, id, ppd > CSS
        printf "    <g class=\"pk%s\"><circle class=\"pt\" r=\"%.2f\"/></g>\n", id, partR > SVG
      }
    }
    print "  </g>" > SVG

    print "    .orb .gh{fill:var(--orbInk)}" > CSS
    print "    .orb .pt{fill:var(--orbInk)}" > CSS
    print "    .orb g[class^=pk]{transform-box:fill-box;transform-origin:center}" > CSS
    print "    @media (prefers-reduced-motion:reduce){" > CSS
    print "      .orb g[class^=pk]{animation:none!important;opacity:.85}" > CSS
    print "    }" > CSS
  }'
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

cp .typecss.tmp .frag.TYPE_CSS
cp .typesvg.tmp .frag.TYPING

# hero: network across the panel, orb sitting in the open space on the right
gen_net 60 24 1244 282 26 7 0 5 .7
gen_orb 1086 150 74
render src/hero.svg assets/hero.svg       "$DARK"
render src/hero.svg assets/hero-light.svg "$LIGHT"
rm -f .typecss.tmp .typesvg.tmp .frag.TYPE_CSS .frag.TYPING

# cta: a sparser network, no orb
gen_net 40 -4 1240 176 18 5 0 3 .45
render src/cta.svg assets/cta.svg       "$DARK"
render src/cta.svg assets/cta-light.svg "$LIGHT"

# ─────────────────────────────────────────────  project cards
# One bespoke animated diagram per project: src/card-<name>.svg

gen_net 60 196 552 432 22 11 0 4 .8
for card in src/card-*.svg; do
  [ -e "$card" ] || continue
  name=$(basename "$card" .svg | sed 's/^card-//')
  render "$card" "assets/projects/$name.svg"       "$DARK"
  render "$card" "assets/projects/$name-light.svg" "$LIGHT"
done

for panel in src/panel-*.svg; do
  [ -e "$panel" ] || continue
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

rm -f .frag.*
