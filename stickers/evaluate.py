#!/usr/bin/env python3
"""
evaluate.py — スタンプ品質評価モジュール

生成されたPNG画像を複数の指標で自動評価し、スコアを返す。

評価指標:
  1. alpha_quality  — 透過品質 (アルファチャンネルの二値化度合い)
  2. character_area — キャラクター占有率 (小さすぎ/はみ出し検出)
  3. clip_score     — CLIPによるプロンプトとの整合性 (任意)
  4. composite      — 上記の重み付き総合スコア

使い方:
  python stickers/evaluate.py stickers/ai_dist/
  python stickers/evaluate.py stickers/ai_dist/ --prompt "cute chibi anime sticker"
"""

import json
import sys
import argparse
import numpy as np
from pathlib import Path
from PIL import Image


def score_alpha_quality(img: Image.Image) -> float:
    """
    透過品質スコア (0.0〜1.0)。
    アルファチャンネルがくっきり二値（0か255）に近いほど高スコア。
    グラデーション・半透明ノイズが多いと低スコア。
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    alpha = np.array(img)[:, :, 3]
    total = alpha.size
    binary = np.sum((alpha == 0) | (alpha == 255))
    return float(binary / total)


def score_character_area(img: Image.Image,
                         min_ratio: float = 0.10,
                         max_ratio: float = 0.85) -> float:
    """
    キャラクター面積スコア (0.0〜1.0)。
    非透明ピクセル割合が min_ratio〜max_ratio に収まると満点。
    小さすぎ/はみ出しを検出する。
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    alpha = np.array(img)[:, :, 3]
    total = alpha.size
    char_pixels = np.sum(alpha > 10)
    ratio = char_pixels / total

    if ratio < min_ratio:
        return ratio / min_ratio  # 小さすぎ → 線形減点
    if ratio > max_ratio:
        return max(0.0, 1.0 - (ratio - max_ratio) / (1.0 - max_ratio))  # はみ出し
    return 1.0


def score_edge_cleanness(img: Image.Image) -> float:
    """
    エッジの綺麗さスコア (0.0〜1.0)。
    アルファチャンネルの境界ピクセル数が少ないほど高スコア
    （ハロー・グリーンスピル残留の検出）。
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    alpha = np.array(img, dtype=np.uint8)[:, :, 3]

    # 境界ピクセル = 値が 1〜254 (半透明)
    semi_transparent = np.sum((alpha > 0) & (alpha < 255))
    total_nonzero = np.sum(alpha > 0)
    if total_nonzero == 0:
        return 0.0

    # 半透明比率が低いほどエッジがくっきり
    semi_ratio = semi_transparent / total_nonzero
    return float(max(0.0, 1.0 - semi_ratio * 3))  # 33%超で0点


def score_clip(img: Image.Image, prompt: str) -> float:
    """
    CLIP スコア (0.0〜1.0)。
    プロンプトと生成画像の意味的整合性を測定。
    transformers が必要 (pip install transformers torch)。
    """
    try:
        import torch
        from transformers import CLIPProcessor, CLIPModel
    except ImportError:
        return -1.0  # 未インストール時はスキップ

    if not hasattr(score_clip, "_model"):
        print("  CLIP モデル読み込み中...", end="", flush=True)
        score_clip._model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        score_clip._processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        score_clip._model.eval()
        print(" 完了")

    model = score_clip._model
    processor = score_clip._processor

    # RGBA → RGB (CLIP は RGB のみ)
    rgb = Image.new("RGB", img.size, (255, 255, 255))
    if img.mode == "RGBA":
        rgb.paste(img, mask=img.split()[3])
    else:
        rgb = img.convert("RGB")

    inputs = processor(text=[prompt], images=[rgb], return_tensors="pt", padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits_per_image  # [1, 1]
        score = torch.sigmoid(logits).item()

    return float(score)


def evaluate_image(
    img_path: Path,
    prompt: str | None = None,
    weights: dict | None = None,
) -> dict:
    """
    1枚の画像を評価してスコア辞書を返す。

    weights: 各指標の重み (デフォルト: alpha=0.4, area=0.3, edge=0.3)
    """
    if weights is None:
        weights = {"alpha": 0.4, "area": 0.3, "edge": 0.3}
        if prompt:
            weights = {"alpha": 0.25, "area": 0.2, "edge": 0.2, "clip": 0.35}

    img = Image.open(img_path).convert("RGBA")

    scores = {
        "alpha_quality":   score_alpha_quality(img),
        "character_area":  score_character_area(img),
        "edge_cleanness":  score_edge_cleanness(img),
    }

    if prompt:
        clip = score_clip(img, prompt)
        scores["clip_score"] = clip if clip >= 0 else None

    # 重み付き総合スコア
    composite = 0.0
    total_weight = 0.0
    mapping = {
        "alpha":  scores["alpha_quality"],
        "area":   scores["character_area"],
        "edge":   scores["edge_cleanness"],
    }
    if prompt and "clip_score" in scores and scores["clip_score"] is not None:
        mapping["clip"] = scores["clip_score"]

    for key, w in weights.items():
        if key in mapping:
            composite += mapping[key] * w
            total_weight += w

    scores["composite"] = composite / total_weight if total_weight > 0 else 0.0
    scores["file"] = str(img_path.name)
    return scores


def evaluate_directory(
    directory: Path,
    prompt: str | None = None,
) -> list[dict]:
    """ディレクトリ内の全 PNG を評価してスコアリストを返す。"""
    results = []
    pngs = sorted(directory.glob("*.png"))
    if not pngs:
        print(f"PNG が見つかりません: {directory}")
        return []

    for png in pngs:
        scores = evaluate_image(png, prompt=prompt)
        results.append(scores)

    return results


def print_report(results: list[dict]) -> None:
    if not results:
        return
    print(f"\n{'ファイル':<35} {'透過':>6} {'面積':>6} {'エッジ':>6} {'総合':>6}")
    print("-" * 65)
    for r in sorted(results, key=lambda x: x["composite"], reverse=True):
        clip_str = f"  CLIP:{r['clip_score']:.2f}" if r.get("clip_score") else ""
        print(
            f"{r['file']:<35} "
            f"{r['alpha_quality']:>6.2f} "
            f"{r['character_area']:>6.2f} "
            f"{r['edge_cleanness']:>6.2f} "
            f"{r['composite']:>6.2f}"
            f"{clip_str}"
        )
    best = max(results, key=lambda x: x["composite"])
    print(f"\n最高スコア: {best['file']}  composite={best['composite']:.3f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="スタンプ品質評価")
    parser.add_argument("directory", help="評価するPNGが入ったディレクトリ")
    parser.add_argument("--prompt", default=None, help="CLIPスコア算出に使うプロンプト")
    args = parser.parse_args()

    results = evaluate_directory(Path(args.directory), prompt=args.prompt)
    print_report(results)
