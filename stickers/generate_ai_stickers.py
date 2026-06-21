#!/usr/bin/env python3
"""
LINEスタンプ AI画像生成スクリプト

【無料で使えるAPI】
  --api huggingface  → FLUX.1-schnell (Hugging Face 無料Inference API, Apache-2.0)
  --api local        → ローカル Stable Diffusion / FLUX (GPU必要、完全無料)

【有料API (高品質)】
  --api gemini  → Nano Banana Pro (gemini-3-pro-image-preview, ~$0.13/枚)
  --api openai  → GPT Image 2 (gpt-image-2, 従量課金)

【背景除去方法】
  --bg-remove rembg      → rembg (AI背景除去、完全ローカル無料) ← 無料APIに最適
  --bg-remove chromakey  → クロマキーグリーン除去 (Gemini/OpenAI API用)

使い方:
  # 無料: Hugging Face FLUX.1-schnell + rembg背景除去
  python stickers/generate_ai_stickers.py --api huggingface

  # 無料: ローカルGPU実行 (VRAM 8GB以上推奨)
  python stickers/generate_ai_stickers.py --api local

  # 有料: Nano Banana Pro
  export GEMINI_API_KEY="..."
  python stickers/generate_ai_stickers.py --api gemini --bg-remove chromakey

  # 有料: GPT Image 2
  export OPENAI_API_KEY="..."
  python stickers/generate_ai_stickers.py --api openai --bg-remove chromakey

  # 1枚だけ試す
  python stickers/generate_ai_stickers.py --api huggingface --ids 01_takubo_normal

  # プロンプト確認のみ (生成しない)
  python stickers/generate_ai_stickers.py --api huggingface --dry-run
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

sys.path.insert(0, str(Path(__file__).parent))
from postprocess import process_sticker_image

SCRIPT_DIR   = Path(__file__).parent
PROMPTS_FILE = SCRIPT_DIR / "prompts.json"
OUTPUT_DIR   = SCRIPT_DIR / "ai_dist"   # --output-dir で上書き可

GEMINI_MODEL = "gemini-3-pro-image-preview"
OPENAI_MODEL = "gpt-image-2"
# FLUX.1-schnell: Apache-2.0ライセンス、商用利用可、無料
HF_MODEL     = "black-forest-labs/FLUX.1-schnell"
# ローカル実行用モデル (diffusers)
LOCAL_MODEL  = "black-forest-labs/FLUX.1-schnell"


# ---------------------------------------------------------------------------
# プロンプト構築
# ---------------------------------------------------------------------------

def build_prompt(sticker: dict, character_style: str, use_chromakey: bool) -> str:
    """
    use_chromakey=True  → #00FF00 背景指定プロンプト (Gemini/OpenAI用)
    use_chromakey=False → 白背景または背景なし指定 (HuggingFace/Local用)
    """
    bg_instruction = (
        "isolated on a FLAT SOLID UNIFORM #00FF00 chromakey green background"
        if use_chromakey
        else "isolated on a plain white background"
    )

    if sticker["id"] in ("06_council_smug", "07_council_angry", "08_takubo_vs_council",
                          "main_cover", "tab_icon"):
        pose = sticker["pose"]
        # 既存の#00FF00指定を白背景に差し替え
        if not use_chromakey:
            pose = pose.replace(
                "on FLAT SOLID #00FF00 green background",
                "on white background"
            ).replace(
                "on a FLAT SOLID #00FF00 green background",
                "on a white background"
            )
        return pose

    style = character_style
    if not use_chromakey:
        style = style.replace(
            "isolated on a FLAT SOLID UNIFORM #00FF00 chromakey green background",
            bg_instruction
        )
    return f"{style} {sticker['pose']}"


# ---------------------------------------------------------------------------
# 無料: Hugging Face Inference API (FLUX.1-schnell)
# ---------------------------------------------------------------------------

def generate_huggingface(prompt: str, sticker_id: str) -> Image.Image:
    """
    Hugging Face 無料 Inference API で FLUX.1-schnell を使用。
    HF_TOKEN 環境変数: 未設定でも動作するが、設定するとレート制限が緩和される。
    無料アカウントでも月2,000リクエストまで利用可能。
    """
    try:
        from huggingface_hub import InferenceClient
    except ImportError:
        sys.exit("ERROR: huggingface_hub が未インストールです。pip install huggingface_hub を実行してください。")

    hf_token = os.environ.get("HF_TOKEN")  # 任意: https://huggingface.co/settings/tokens で無料取得
    client = InferenceClient(token=hf_token)

    # FLUX.1-schnell は横長 (LINEスタンプ比率に近い) を生成
    is_square = sticker_id in ("main_cover", "tab_icon")
    width, height = (768, 768) if is_square else (896, 768)

    img_bytes = client.text_to_image(
        prompt=prompt,
        model=HF_MODEL,
        width=width,
        height=height,
        num_inference_steps=4,  # schnell は4ステップで高品質
    )

    if isinstance(img_bytes, Image.Image):
        return img_bytes
    return Image.open(io.BytesIO(img_bytes))


# ---------------------------------------------------------------------------
# 無料: ローカル GPU 実行 (FLUX.1-schnell via diffusers)
# ---------------------------------------------------------------------------

def generate_local(prompt: str, sticker_id: str) -> Image.Image:
    """
    ローカルGPUで FLUX.1-schnell を実行。完全無料・制限なし。
    初回: モデルファイル (~23GB) を自動ダウンロード。
    VRAM: 8GB以上推奨 (12GB以上で快適)。
    """
    try:
        import torch
        from diffusers import FluxPipeline
    except ImportError:
        sys.exit(
            "ERROR: diffusers/torch が未インストールです。\n"
            "pip install diffusers torch transformers accelerate を実行してください。"
        )

    if not hasattr(generate_local, "_pipe"):
        print("  モデル読み込み中 (初回のみ)...", end="", flush=True)
        pipe = FluxPipeline.from_pretrained(
            LOCAL_MODEL,
            torch_dtype=torch.bfloat16,
        )
        pipe.enable_model_cpu_offload()
        generate_local._pipe = pipe
        print(" 完了")

    is_square = sticker_id in ("main_cover", "tab_icon")
    width, height = (768, 768) if is_square else (896, 768)

    result = generate_local._pipe(
        prompt=prompt,
        guidance_scale=0.0,   # schnell は CFG不要
        num_inference_steps=4,
        width=width,
        height=height,
    )
    return result.images[0]


# ---------------------------------------------------------------------------
# 有料: Nano Banana Pro (Gemini 3 Pro Image)
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
# 有料: GPT Image 2 (OpenAI)
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
    size = "1024x1024" if sticker_id in ("main_cover", "tab_icon") else "1536x1024"

    response = client.images.generate(
        model=OPENAI_MODEL,
        prompt=prompt,
        n=1,
        size=size,
        quality="high",
        response_format="b64_json",
    )

    img_b64 = response.data[0].b64_json
    return Image.open(io.BytesIO(base64.b64decode(img_b64)))


# ---------------------------------------------------------------------------
# API設定マップ
# ---------------------------------------------------------------------------

API_CONFIG = {
    "huggingface": {
        "fn":          generate_huggingface,
        "label":       "FLUX.1-schnell (Hugging Face 無料API)",
        "chromakey":   False,   # 白背景で生成 → rembg で除去
        "default_bg":  "rembg",
    },
    "local": {
        "fn":          generate_local,
        "label":       "FLUX.1-schnell (ローカルGPU・完全無料)",
        "chromakey":   False,
        "default_bg":  "rembg",
    },
    "gemini": {
        "fn":          generate_gemini,
        "label":       "Nano Banana Pro (Gemini 3 Pro Image) ※有料",
        "chromakey":   True,
        "default_bg":  "chromakey",
    },
    "openai": {
        "fn":          generate_openai,
        "label":       "GPT Image 2 (OpenAI) ※有料",
        "chromakey":   True,
        "default_bg":  "chromakey",
    },
}


# ---------------------------------------------------------------------------
# メイン処理
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="LINEスタンプ AI画像生成スクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--api",
        choices=list(API_CONFIG.keys()),
        required=True,
        help="生成API: huggingface (無料) / local (無料GPU) / gemini (有料) / openai (有料)",
    )
    parser.add_argument(
        "--bg-remove",
        choices=["rembg", "chromakey"],
        default=None,
        help="背景除去方法 (省略時はAPIに応じて自動選択: 無料API→rembg, 有料API→chromakey)",
    )
    parser.add_argument("--ids", nargs="*", default=None,
                        help="生成するスタンプIDを指定（省略時は全件）")
    parser.add_argument("--dry-run", action="store_true",
                        help="プロンプトを表示するだけで実際には生成しない")
    parser.add_argument("--retry", type=int, default=3,
                        help="失敗時のリトライ回数（デフォルト: 3）")
    parser.add_argument("--output-dir", default=None,
                        help="出力ディレクトリ (省略時は stickers/ai_dist/)")
    parser.add_argument("--bg-model", default=None,
                        help="rembg使用時の背景除去モデル名 (例: isnet-anime, birefnet-general)")
    parser.add_argument("--lora", default=None,
                        help="使用するLoRAモデルID (ローカル実行時のみ有効)")
    parser.add_argument("--lora-trigger", default=None,
                        help="LoRAのトリガーワード")
    args = parser.parse_args()

    cfg = API_CONFIG[args.api]
    bg_remove = args.bg_remove or cfg["default_bg"]
    use_chromakey = cfg["chromakey"]

    # --output-dir が指定された場合は上書き
    global OUTPUT_DIR
    if args.output_dir:
        OUTPUT_DIR = Path(args.output_dir)

    with open(PROMPTS_FILE, encoding="utf-8") as f:
        data = json.load(f)

    character_style = data["character_style"]
    stickers = data["stickers"]

    if args.ids:
        stickers = [s for s in stickers if s["id"] in args.ids]
        if not stickers:
            sys.exit(f"ERROR: 指定されたIDが見つかりません: {args.ids}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"API        : {cfg['label']}")
    print(f"背景除去   : {bg_remove}")
    print(f"生成件数   : {len(stickers)} 枚")
    print(f"出力先     : {OUTPUT_DIR}\n")

    for i, sticker in enumerate(stickers, 1):
        sid     = sticker["id"]
        label   = sticker["label"]
        prompt  = build_prompt(sticker, character_style, use_chromakey)
        outpath = OUTPUT_DIR / f"{sid}.png"

        print(f"[{i}/{len(stickers)}] {label} ({sid})")

        if args.dry_run:
            print(f"  [DRY-RUN] プロンプト:\n  {prompt}\n")
            continue

        for attempt in range(1, args.retry + 1):
            try:
                print(f"  生成中... (試行 {attempt}/{args.retry})", end="", flush=True)
                raw_img = cfg["fn"](prompt, sid)
                print(" 完了")

                print(f"  後処理 ({bg_remove} + リサイズ)...", end="", flush=True)
                bg_model = getattr(args, "bg_model", None)
                processed = process_sticker_image(raw_img, sid, bg_remove=bg_remove,
                                                   bg_model=bg_model)
                processed.save(outpath, "PNG")
                size_kb = outpath.stat().st_size / 1024
                print(f" 完了 → {outpath.name} ({size_kb:.1f} KB)")

                if size_kb > 500:
                    print(f"  警告: {size_kb:.0f} KB はLINE上限500KBを超えています。")
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
