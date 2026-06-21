#!/usr/bin/env python3
"""
research.py — 外部情報収集モジュール

HuggingFace Hub + GitHub から最新のLoRAモデル・技術を自動収集し、
knowledge_base.json を更新する。

使い方:
  python stickers/research.py              # 知識ベース更新のみ
  python stickers/research.py --report     # 更新内容をコンソールに表示
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR     = Path(__file__).parent
KNOWLEDGE_FILE = SCRIPT_DIR / "knowledge_base.json"

# HuggingFace 検索クエリ（ダウンロード数降順）
HF_SEARCH_QUERIES = [
    {"search": "sticker flux lora",  "tags": ["lora"]},
    {"search": "anime chibi flux",   "tags": ["lora"]},
    {"search": "line sticker",       "tags": ["lora"]},
]

# 背景除去モデル: rembg でサポートされるモデル名
# isnet-anime が LINEスタンプ(アニメ系)に最も適している
REMBG_MODELS_PRIORITY = [
    ("isnet-anime",       "アニメ・イラスト特化 SOTA"),
    ("birefnet-general",  "汎用 SOTA、エッジ精度最高"),
    ("u2net",             "高速・汎用"),
]

# 参照する GitHub リポジトリ（API不要で固定情報として保持）
GITHUB_REFS = [
    {
        "repo": "philschmid/gemini-samples",
        "url":  "https://github.com/philschmid/gemini-samples",
        "key_technique": "chromakey + HSV mask removal for Gemini Nano Banana Pro",
        "notebook": "examples/interactions-generate-stickers.ipynb",
    },
    {
        "repo": "skyiron/stickerkitComfyui",
        "url":  "https://github.com/skyiron/stickerkitComfyui",
        "key_technique": "FLUX.1 + PuLID for character consistency sticker generation",
    },
    {
        "repo": "1038lab/ComfyUI-RMBG",
        "url":  "https://github.com/1038lab/ComfyUI-RMBG",
        "key_technique": "RMBG-2.0, BiRefNet, BEN2 ensemble background removal",
    },
    {
        "repo": "rootonchair/diffuser_layerdiffuse",
        "url":  "https://github.com/rootonchair/diffuser_layerdiffuse",
        "key_technique": "Layer Diffusion: native transparent image generation with diffusers",
    },
]


def load_knowledge_base() -> dict:
    if KNOWLEDGE_FILE.exists():
        with open(KNOWLEDGE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"lora_models": [], "bg_removal_models": [], "prompt_strategies": [],
            "github_workflows": [], "evaluation_history": []}


def save_knowledge_base(kb: dict) -> None:
    kb["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)


def fetch_hf_lora_models(limit: int = 10) -> list[dict]:
    """
    HuggingFace Hub API でスタンプ向けLoRAモデルを検索し、
    ダウンロード数でソートして返す。
    """
    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("  [WARN] huggingface_hub 未インストール。LoRAモデル検索をスキップ。")
        return []

    api = HfApi()
    discovered: dict[str, dict] = {}

    for query in HF_SEARCH_QUERIES:
        try:
            models = list(api.list_models(
                search=query["search"],
                sort="downloads",
                limit=limit,
                expand=["downloads", "tags", "cardData"],
            ))
            for m in models:
                mid = m.modelId
                if mid in discovered:
                    continue
                # FLUX/LoRA ベースかどうかモデルIDで判定
                mid_lower = mid.lower()
                tags = [t.lower() for t in (getattr(m, "tags", None) or [])]
                is_flux_lora = (
                    any(k in mid_lower for k in ["flux", "lora", "sticker", "anime", "chibi"])
                    or any(t in tags for t in ["lora", "flux"])
                )
                if not is_flux_lora:
                    continue
                discovered[mid] = {
                    "id":           mid,
                    "trigger_word": _guess_trigger(mid),
                    "style_tags":   _extract_style_tags(tags),
                    "base_model":   "flux",
                    "license":      getattr(m, "license", "unknown"),
                    "source":       "huggingface",
                    "downloads":    getattr(m, "downloads", 0) or 0,
                    "notes":        f"HuggingFace 検索で発見: '{query['search']}'",
                }
        except Exception as e:
            print(f"  [WARN] HF検索エラー ({query['search']}): {e}")

    # ダウンロード数降順でランク付け
    sorted_models = sorted(discovered.values(), key=lambda x: x["downloads"], reverse=True)
    for i, m in enumerate(sorted_models, 1):
        m["rank"] = i
    return sorted_models


def _guess_trigger(model_id: str) -> str:
    """モデルIDからトリガーワードを推測する。"""
    lower = model_id.lower()
    if "ton618" in lower:
        return "TON618"
    if "sticker" in lower:
        return "sticker"
    if "anime" in lower:
        return "anime style"
    if "chibi" in lower:
        return "chibi"
    return model_id.split("/")[-1].replace("-", " ")


def _extract_style_tags(tags: list[str]) -> list[str]:
    style_keywords = {"sticker", "anime", "chibi", "cartoon", "illustration",
                      "flat", "outline", "kawaii", "cute"}
    return [t for t in tags if t in style_keywords]


def merge_lora_models(existing: list[dict], discovered: list[dict]) -> list[dict]:
    """
    既存リストに新規発見モデルをマージ（既存優先、新規を末尾に追加）。
    """
    existing_ids = {m["id"] for m in existing}
    merged = list(existing)
    for m in discovered:
        if m["id"] not in existing_ids:
            merged.append(m)
            print(f"  [NEW] LoRA追加: {m['id']}")
    # ダウンロード数でランク更新
    for i, m in enumerate(merged, 1):
        m["rank"] = i
    return merged


def update_github_refs(kb: dict) -> None:
    """GitHub参照リストを最新の既知情報で更新する。"""
    existing_repos = {w["repo"] for w in kb.get("github_workflows", [])}
    for ref in GITHUB_REFS:
        if ref["repo"] not in existing_repos:
            kb["github_workflows"].append({
                "repo":          ref["repo"],
                "description":   ref.get("key_technique", ""),
                "url":           ref["url"],
                "key_technique": ref.get("key_technique", ""),
            })
            print(f"  [NEW] GitHub参照追加: {ref['repo']}")


def run(report: bool = False) -> dict:
    print("=== research.py: 知識ベース更新 ===\n")
    kb = load_knowledge_base()

    # 1. HuggingFace LoRA モデル検索
    print("[1/3] HuggingFace Hub でLoRAモデルを検索中...")
    discovered = fetch_hf_lora_models(limit=8)
    print(f"  発見: {len(discovered)} モデル")
    kb["lora_models"] = merge_lora_models(kb.get("lora_models", []), discovered)

    # 2. GitHub 参照更新
    print("\n[2/3] GitHub参照リストを更新中...")
    update_github_refs(kb)

    # 3. 背景除去モデルのベストプラクティスを更新
    print("\n[3/3] 背景除去モデルの優先順を確認...")
    bg_ids = {m["id"] for m in kb.get("bg_removal_models", [])}
    for model_name, desc in REMBG_MODELS_PRIORITY:
        entry_id = f"rembg/{model_name}"
        if entry_id not in bg_ids:
            kb["bg_removal_models"].append({
                "id":         entry_id,
                "method":     "rembg",
                "model_name": model_name,
                "quality":    "excellent",
                "speed":      "medium",
                "notes":      desc,
            })
            print(f"  [NEW] bg_removal追加: {entry_id}")

    save_knowledge_base(kb)
    print(f"\n知識ベースを更新しました: {KNOWLEDGE_FILE}")

    if report:
        print("\n--- 現在の知識ベース ---")
        print(f"LoRAモデル ({len(kb['lora_models'])}件):")
        for m in kb["lora_models"][:5]:
            dl = m.get("downloads", "?")
            print(f"  #{m.get('rank','?')} {m['id']}  (DL:{dl})")
        print(f"\n背景除去モデル ({len(kb['bg_removal_models'])}件):")
        for m in kb["bg_removal_models"]:
            print(f"  {m['id']}  - {m.get('notes','')}")
        print(f"\nGitHub参照 ({len(kb['github_workflows'])}件):")
        for w in kb["github_workflows"]:
            print(f"  {w['repo']}")

    return kb


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="外部情報収集・知識ベース更新")
    parser.add_argument("--report", action="store_true", help="更新内容をコンソールに詳細表示")
    args = parser.parse_args()
    run(report=args.report)
