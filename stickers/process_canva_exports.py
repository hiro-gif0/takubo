#!/usr/bin/env python3
"""
Canva エクスポート後処理スクリプト

Canva (Free プラン) は透過PNGを直接エクスポートできないため、
白背景PNGをダウンロードしたあとこのスクリプトで背景除去 + リサイズを行う。

使い方:
  python stickers/process_canva_exports.py

  入力: stickers/canva_raw/*.png  (Canva からダウンロードした白背景PNG)
  出力: stickers/ai_dist/*.png    (透過PNG, LINE規定サイズ)

必要なパッケージ:
  pip install rembg onnxruntime Pillow
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from postprocess import remove_background_rembg, resize_for_line

RAW_DIR  = Path(__file__).parent / "canva_raw"
OUT_DIR  = Path(__file__).parent / "ai_dist"

LINE_SIZE = (370, 320)
MAIN_SIZE = (240, 240)
TAB_SIZE  = (96, 74)

SIZE_MAP = {
    "main_cover": MAIN_SIZE,
    "tab_icon":   TAB_SIZE,
}


def main():
    from PIL import Image

    if not RAW_DIR.exists() or not list(RAW_DIR.glob("*.png")):
        print(f"ERROR: {RAW_DIR} にPNGファイルがありません。")
        print("Canva からダウンロードしたPNGをそこに置いてください。")
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(RAW_DIR.glob("*.png"))
    print(f"=== Canva エクスポート後処理 ({len(files)} ファイル) ===\n")

    for raw in files:
        sid = raw.stem
        out = OUT_DIR / f"{sid}.png"
        target = SIZE_MAP.get(sid, LINE_SIZE)
        print(f"  {sid}  ({target[0]}x{target[1]}) ...", end="", flush=True)

        img = Image.open(raw)
        img = remove_background_rembg(img, model_name="isnet-anime")
        img = resize_for_line(img, target)
        img.save(out, "PNG")

        kb = out.stat().st_size / 1024
        warn = "  ⚠ 500KB超" if kb > 500 else ""
        print(f" OK  ({kb:.0f} KB){warn}")

    print(f"\n完了 → {OUT_DIR}")
    pngs = sorted(OUT_DIR.glob("*.png"))
    for p in pngs:
        print(f"  {p.name}  ({p.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
