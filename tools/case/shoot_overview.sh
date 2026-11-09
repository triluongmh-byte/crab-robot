#!/bin/sh
# Headless Chrome screenshots of case/overview.html states (visual check). usage: shoot_overview.sh
set -e
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUTD="$ROOT/build/case/shots"; mkdir -p "$OUTD"
F="file://$ROOT/case/overview.html"
shot() { "$CH" --headless=new --no-sandbox --use-angle=swiftshader --enable-unsafe-swiftshader --hide-scrollbars \
  --user-data-dir="$ROOT/build/case/chrome-$1" --window-size=$2 --virtual-time-budget=5000 \
  --screenshot="$OUTD/$1.png" "$F#$3" >/dev/null 2>&1; }
shot full 1400,1000 "theme=light" &
shot step3 1400,1000 "step=3&focus=C1" &
shot phone 390,1700 "step=6" &
shot dark 1400,1000 "theme=dark&step=8&cam=front" &
shot top 1400,1000 "cam=top" &
shot detail 390,2400 "step=4&detail=1&hip=25&knee=-25" &
wait
ls "$OUTD"
