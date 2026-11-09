#!/bin/sh
# Exports case/images/{top,front,iso,exploded}.png from the current case/overview.html (headless Chrome).
set -e
ROOT=$(cd "$(dirname "$0")/../.." && pwd); mkdir -p "$ROOT/case/images"
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"; F="file://$ROOT/case/overview.html"
shot() { "$CH" --headless=new --no-sandbox --use-angle=swiftshader --enable-unsafe-swiftshader --hide-scrollbars \
  --user-data-dir="$ROOT/build/case/chrome-img-$1" --window-size=1400,1000 --virtual-time-budget=5000 \
  --screenshot="$ROOT/case/images/$1.png" "$F#$2" >/dev/null 2>&1; }
shot top "cam=top" & shot front "cam=front" & shot iso "cam=iso" & shot exploded "explode=40&cam=iso" & wait
ls -la "$ROOT/case/images"
