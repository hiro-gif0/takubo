#!/usr/bin/env python3
"""
LINEスタンプ AI画像生成スクリプト

対応API:
  --api gemini  → Nano Banana Pro (gemini-3-pro-image-preview)
  --api openai  → GPT Image 2 (gpt-image-2)

どちらもクロマキーグリーン (#00FF00) 背景で生成し、
postprocess.py で透過PNGに変換してLINE規定サイズに整形する。

使い方:
  export GEMINI_API_KEY="..."   # Nano Banana Pro用
  export OPENAI_API_KEY="..."   # GPT Image 2用

  python stickers/generate_ai_stickers.py --api gemini
  python stickers/generate_ai_stickers.py --api openai
  python stickers/generate_ai_stickers.py --api gemini --ids 01_takubo_normal 02_takubo_victory
  python stickers/generate_ai_stickers.py --api openai --dry-run
"""

import argparse
import base64
import io
import json
import os
import sys
import time
from pathlib import Path

from PIL import Image

# postprocess.py は同ディレクトリ
sys.path.insert(0, str(Path(__file__).parent))
from postprocess import process_sticker_image

# ---- パス設定 ----
SCRIPT_DIR   = Path(__file__).parent
PROMPTS_FILE = SCRIPT_DIR / "prompts.json"
OUTPUT_DIR   = SCRIPT_DIR / "ai_dist"

# ---- モデル設定 ----
GEMINI_MODEL = "gemini-3-pro-image-preview"
OPENAI_MODEL = "gpt-image-2"

# ---- 画像サイズ (API側生成サイズ) ----
GEMINI_ASPECT = "16:14"       # 横長 (370:320 ≈ 16:14)
OPENAI_SIZE_DEFAULT = "1024x896"  # 近似比率 (gpt-image-2 は 1024x1024, 1536x1024, 1024x1536 のみ)
OPENAI_SIZE_SQUARE  = "1024x1024"


# ---------------------------------------------------------------------------
# プロンプト構築
# ---------------------------------------------------------------------------

def build_prompt(sticker: dict, character_style: str) -> str:
    if sticker["id"] in ("06_council_smug", "07_council_angry", "08_takubo_vs_council",
                          "main_cover", "tab_icon"):
        # これらは pose の中にスタイル指定が含まれている
        return sticker["pose"]
    return f"{character_style} {sticker['pose']}"


# ---------------------------------------------------------------------------
# Nano Banana Pro (Gemini 3 Pro Image)
# ---------------------------------------------------------------------------

def generate_gemini(prompt: str, sticker_id: str) -> Image.Image:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        sys.exit("ERROR: google-genai が未インストールです。pip install google-genai を実行してください。")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("ERROR: 環境変数 GEMINI_API_KEY が設定されていません。")

    client = genai.Client(api_key=api_key)

    size = sticker.get("size", None) if isinstance(sticker, dict) else None

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        ),
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            return Image.open(io.BytesIO(part.inline_data.data))

    raise RuntimeError("Gemini から画像データが返却されませんでした。")


# ---------------------------------------------------------------------------
# GPT Image 2 (OpenAI)
# ---------------------------------------------------------------------------

def generate_openai(prompt: str, sticker_id: str) -> Image.Image:
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("ERROR: openai が未インストールです。pip install openai を実行してください。")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        sys.exit("ERROR: 環境変数 OPENAI_API_KEY が設定されていません。")

    client = OpenAI(api_key=api_key)

    # gpt-image-2 は 1024x1024 / 1536x1024 / 1024x1536 のみサポート
    size = OPENAI_SIZE_SQUARE if sticker_id in ("main_cover", "tab_icon") else "1536x1024"

    response = client.images.generate(
        model=OPENAI_MODEL,
        prompt=prompt,
        n=1,
        size=size,
        output_format="png",
        quality="high",
    )

    img_b64 = response.data[0].b64_json
    return Image.open(io.BytesIO(base64.b64decode(img_b64)))


# ---------------------------------------------------------------------------
# メイン処理
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LINEスタンプ AI画像生成スクリプト")
    parser.add_argument("--api", choices=["gemini", "openai"], required=True,
                        help="使用するAPI: gemini (Nano Banana Pro) または openai (GPT Image 2)")
    parser.add_argument("--ids", nargs="*", default=None,
                        help="生成するスタンプIDを指定（省略時は全件）")
    parser.add_argument("--dry-run", action="store_true",
                        help="プロンプトを表示するだけで実際には生成しない")
    parser.add_argument("--retry", type=int, default=3,
                        help="失敗時のリトライ回数（デフォルト: 3）")
    args = parser.parse_args()

    # プロンプト定義読み込み
    with open(PROMPTS_FILE, encoding="utf-8") as f:
        data = json.load(f)

    character_style = data["character_style"]
    stickers = data["stickers"]

    # ID フィルタ
    if args.ids:
        stickers = [s for s in stickers if s["id"] in args.ids]
        if not stickers:
            sys.exit(f"ERROR: 指定されたIDが見つかりません: {args.ids}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    generate_fn = generate_gemini if args.api == "gemini" else generate_openai

    print(f"API: {'Nano Banana Pro (Gemini 3 Pro Image)' if args.api == 'gemini' else 'GPT Image 2 (OpenAI)'}")
    print(f"生成件数: {len(stickers)} 枚\n")

    for i, sticker in enumerate(stickers, 1):
        sid    = sticker["id"]
        label  = sticker["label"]
        prompt = build_prompt(sticker, character_style)
        outpath = OUTPUT_DIR / f"{sid}.png"

        print(f"[{i}/{len(stickers)}] {label} ({sid})")

        if args.dry_run:
            print(f"  [DRY-RUN] プロンプト:\n  {prompt}\n")
            continue

        # リトライループ
        for attempt in range(1, args.retry + 1):
            try:
                print(f"  生成中... (試行 {attempt}/{args.retry})", end="", flush=True)
                raw_img = generate_fn(prompt, sid)
                print(" 完了")

                # クロマキー除去 + リサイズ
                print("  後処理（クロマキー除去・リサイズ）...", end="", flush=True)
                processed = process_sticker_image(raw_img, sid)
                processed.save(outpath, "PNG")
                size_kb = outpath.stat().st_size / 1024
                print(f" 完了 → {outpath.name} ({size_kb:.1f} KB)")

                if size_kb > 500:
                    print(f"  ⚠️  警告: {size_kb:.0f} KB はLINE上限 500 KB を超えています。")
                break

            except Exception as e:
                print(f" 失敗: {e}")
                if attempt < args.retry:
                    wait = 2 ** attempt
                    print(f"  {wait}秒後にリトライ...")
                    time.sleep(wait)
                else:
                    print(f"  スキップ: {sid}")

        print()

    if not args.dry_run:
        print("=== 完了 ===")
        pngs = list(OUTPUT_DIR.glob("*.png"))
        print(f"出力先: {OUTPUT_DIR}")
        for p in sorted(pngs):
            print(f"  {p.name}  ({p.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
