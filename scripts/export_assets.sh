#!/usr/bin/env bash
set -euo pipefail

SRC="dist/chatgpt_image2_seminar_flyer_a4.svg"
PNG="dist/chatgpt_image2_seminar_flyer_a4.png"
PDF="dist/chatgpt_image2_seminar_flyer_a4.pdf"

if [[ ! -f "$SRC" ]]; then
  echo "ERROR: $SRC が見つかりません。"
  exit 1
fi

ok=0

if command -v inkscape >/dev/null 2>&1; then
  inkscape "$SRC" --export-type=png --export-filename="$PNG" --export-dpi=300
  inkscape "$SRC" --export-type=pdf --export-filename="$PDF"
  ok=1
elif command -v rsvg-convert >/dev/null 2>&1; then
  rsvg-convert -f png -o "$PNG" -w 2480 -h 3508 "$SRC"
  rsvg-convert -f pdf -o "$PDF" "$SRC"
  ok=1
elif command -v magick >/dev/null 2>&1; then
  magick -density 300 "$SRC" "$PNG"
  magick "$SRC" "$PDF"
  ok=1
elif command -v convert >/dev/null 2>&1; then
  convert -density 300 "$SRC" "$PNG"
  convert "$SRC" "$PDF"
  ok=1
elif command -v cairosvg >/dev/null 2>&1; then
  cairosvg "$SRC" -o "$PNG" --output-width 2480 --output-height 3508
  cairosvg "$SRC" -o "$PDF"
  ok=1
fi

if [[ "$ok" -eq 1 ]]; then
  echo "OK: PNG/PDFを生成しました。"
  ls -lh "$PNG" "$PDF"
else
  echo "WARNING: 変換ツールが見つからないためPNG/PDFを生成できませんでした。"
  echo "利用可能ツール例: inkscape / rsvg-convert / magick / cairosvg"
  exit 2
fi
