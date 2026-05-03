#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="stickers/src"
DIST_DIR="stickers/dist"

mkdir -p "$DIST_DIR"

# 変換ツールを検出
TOOL=""
if   command -v inkscape      >/dev/null 2>&1; then TOOL="inkscape"
elif command -v rsvg-convert  >/dev/null 2>&1; then TOOL="rsvg-convert"
elif command -v magick        >/dev/null 2>&1; then TOOL="magick"
elif command -v convert       >/dev/null 2>&1; then TOOL="convert"
elif command -v cairosvg      >/dev/null 2>&1; then TOOL="cairosvg"
fi

if [[ -z "$TOOL" ]]; then
  echo "ERROR: 変換ツールが見つかりません。inkscape / rsvg-convert / magick / cairosvg のいずれかをインストールしてください。"
  exit 1
fi
echo "使用ツール: $TOOL"

# SVG → PNG 変換関数
convert_svg() {
  local src="$1" dst="$2" w="$3" h="$4"
  case "$TOOL" in
    inkscape)
      inkscape "$src" --export-type=png --export-filename="$dst" \
               --export-width="$w" --export-height="$h"
      ;;
    rsvg-convert)
      rsvg-convert -f png -o "$dst" -w "$w" -h "$h" "$src"
      ;;
    magick|convert)
      "$TOOL" -background none -resize "${w}x${h}" "$src" "$dst"
      ;;
    cairosvg)
      cairosvg "$src" -o "$dst" --output-width "$w" --output-height "$h"
      ;;
  esac
}

# スタンプ画像 (370x320) — main_cover と tab_icon 以外
echo ""
echo "=== スタンプ画像 (370x320) ==="
for svg in "$SRC_DIR"/[0-9][0-9]_*.svg; do
  [[ -f "$svg" ]] || continue
  base=$(basename "$svg" .svg)
  dst="$DIST_DIR/${base}.png"
  echo "  $svg → $dst"
  convert_svg "$svg" "$dst" 370 320
done

# メイン画像 (240x240)
echo ""
echo "=== メイン画像 (240x240) ==="
convert_svg "$SRC_DIR/main_cover.svg" "$DIST_DIR/main.png" 240 240
echo "  $SRC_DIR/main_cover.svg → $DIST_DIR/main.png"

# タブ画像 (96x74)
echo ""
echo "=== タブ画像 (96x74) ==="
convert_svg "$SRC_DIR/tab_icon.svg" "$DIST_DIR/tab.png" 96 74
echo "  $SRC_DIR/tab_icon.svg → $DIST_DIR/tab.png"

echo ""
echo "=== 完了 ==="
ls -lh "$DIST_DIR"/*.png
