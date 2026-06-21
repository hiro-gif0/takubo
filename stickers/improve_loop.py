#!/usr/bin/env python3
"""
improve_loop.py — 改善ループ オーケストレーター

【処理フロー】
  Phase 1: Research  — HuggingFace/GitHub から最新LoRA・技術を収集
  Phase 2: Configure — 知識ベースから複数の生成設定を構築
  Phase 3: Generate  — 各設定でテスト用スタンプを生成
  Phase 4: Evaluate  — 透過品質・面積・CLIP スコアで自動評価
  Phase 5: Select    — 最高スコアの設定を採用し prompts.json / configs/ を更新
  Phase 6: Loop      — 指定回数繰り返して収束させる

使い方:
  # 無料 API でループ3回実行
  python stickers/improve_loop.py --api huggingface --iterations 3

  # 1枚だけテストして最適設定を探す
  python stickers/improve_loop.py --api huggingface --test-id 01_takubo_normal --iterations 2

  # 研究フェーズのみ実行（生成なし）
  python stickers/improve_loop.py --research-only
"""

import argparse
import json
import subprocess
import sys
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

SCRIPT_DIR     = Path(__file__).parent
PROMPTS_FILE   = SCRIPT_DIR / "prompts.json"
KB_FILE        = SCRIPT_DIR / "knowledge_base.json"
RESULTS_DIR    = SCRIPT_DIR / "results"
CONFIGS_DIR    = SCRIPT_DIR / "configs"
OUTPUT_DIR     = SCRIPT_DIR / "ai_dist"

sys.path.insert(0, str(SCRIPT_DIR))
from evaluate import evaluate_image, evaluate_directory, print_report
import research


# ---------------------------------------------------------------------------
# 設定ビルダー — 知識ベースから複数の実験設定を生成
# ---------------------------------------------------------------------------

def build_experiment_configs(kb: dict, api: str) -> list[dict]:
    """
    知識ベースから実験設定リストを構築する。
    各設定は (bg_model, lora_id, prompt_template) の組み合わせ。
    """
    configs = []

    # 背景除去モデルの候補 (品質 excellent のもの優先)
    bg_candidates = [
        m for m in kb.get("bg_removal_models", [])
        if m.get("quality") in ("excellent", "good")
        and m.get("method") == ("chromakey" if api in ("gemini", "openai") else "rembg")
    ]
    if not bg_candidates:
        bg_candidates = [{"id": "rembg/isnet-anime", "method": "rembg",
                          "model_name": "isnet-anime"}]

    # LoRA 候補 (rank 上位3まで、local のみ)
    lora_candidates = [None]  # None = LoRAなし (ベースライン)
    if api == "local":
        top_loras = sorted(kb.get("lora_models", []),
                           key=lambda x: x.get("rank", 999))[:3]
        lora_candidates += top_loras

    # プロンプト戦略の候補
    prompt_strategies = kb.get("prompt_strategies", [])
    if not prompt_strategies:
        prompt_strategies = [{"name": "default", "template": None}]

    # 組み合わせ生成 (最大6設定まで)
    for bg in bg_candidates[:2]:
        for lora in lora_candidates[:2]:
            for ps in prompt_strategies[:2]:
                config = {
                    "id":              f"{bg['id'].split('/')[-1]}__{lora['id'].split('/')[-1] if lora else 'no-lora'}__{ps['name']}",
                    "api":             api,
                    "bg_remove":       bg.get("method", "rembg"),
                    "bg_model":        bg.get("model_name"),
                    "lora":            lora,
                    "prompt_strategy": ps,
                    "scores":          None,
                }
                configs.append(config)
                if len(configs) >= 6:
                    return configs

    return configs


# ---------------------------------------------------------------------------
# プロンプト生成 — 設定 + 知識ベースを合わせて最適プロンプトを構築
# ---------------------------------------------------------------------------

def build_prompt_from_config(sticker: dict, base_style: str, config: dict) -> str:
    """
    実験設定に応じてプロンプトを組み立てる。
    """
    ps = config.get("prompt_strategy") or {}
    template = ps.get("template")
    lora = config.get("lora")
    use_chromakey = config.get("bg_remove") == "chromakey"

    if use_chromakey:
        bg_str = "isolated on a FLAT SOLID UNIFORM #00FF00 chromakey green background"
    else:
        bg_str = "isolated on a plain white background"

    trigger = lora["trigger_word"] if lora else ""
    quality_mod = ps.get("quality_modifier", "high quality, clean lines")

    if template:
        char_desc = "elderly Japanese woman politician with short white hair, orange blazer, navy skirt"
        prompt = template.format(
            character_desc=char_desc,
            pose_desc=sticker.get("pose", ""),
        )
        if trigger:
            prompt = f"{trigger}, {prompt}"
        if quality_mod:
            prompt = f"{prompt}, {quality_mod}"
        return prompt

    # デフォルト: 既存 character_style を使用
    style = base_style.replace(
        "isolated on a FLAT SOLID UNIFORM #00FF00 chromakey green background",
        bg_str,
    )
    if trigger:
        style = f"{trigger}, {style}"
    return f"{style} {sticker.get('pose', '')}"


# ---------------------------------------------------------------------------
# Phase 3: 生成
# ---------------------------------------------------------------------------

def run_generation(config: dict, test_ids: list[str] | None) -> Path:
    """指定の設定でスタンプを生成し、出力ディレクトリを返す。"""
    run_dir = RESULTS_DIR / config["id"]
    run_dir.mkdir(parents=True, exist_ok=True)

    # generate_ai_stickers.py を subprocess で実行
    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "generate_ai_stickers.py"),
        "--api", config["api"],
        "--bg-remove", config["bg_remove"],
        "--output-dir", str(run_dir),
    ]
    if test_ids:
        cmd += ["--ids"] + test_ids

    bg_model = config.get("bg_model")
    if bg_model:
        cmd += ["--bg-model", bg_model]

    lora = config.get("lora")
    if lora:
        cmd += ["--lora", lora["id"], "--lora-trigger", lora.get("trigger_word", "")]

    print(f"  実行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [ERROR] 生成失敗:\n{result.stderr[:500]}")
    else:
        print(result.stdout[-300:] if result.stdout else "")

    return run_dir


# ---------------------------------------------------------------------------
# Phase 4 & 5: 評価 + 最良設定選択
# ---------------------------------------------------------------------------

def evaluate_run(run_dir: Path, test_prompt: str | None) -> dict:
    """1設定の生成結果を評価し、集計スコアを返す。"""
    results = evaluate_directory(run_dir, prompt=test_prompt)
    if not results:
        return {"composite_avg": 0.0, "details": []}

    avg = sum(r["composite"] for r in results) / len(results)
    return {
        "composite_avg": avg,
        "count":         len(results),
        "details":       results,
    }


def select_best_config(configs: list[dict]) -> dict | None:
    """スコア済み設定リストから最良を返す。"""
    scored = [c for c in configs if c.get("scores") and c["scores"].get("composite_avg", 0) > 0]
    if not scored:
        return None
    return max(scored, key=lambda c: c["scores"]["composite_avg"])


def update_prompts_with_best(best_config: dict) -> None:
    """最良設定の情報を prompts.json に反映する。"""
    with open(PROMPTS_FILE, encoding="utf-8") as f:
        data = json.load(f)

    ps = best_config.get("prompt_strategy") or {}
    lora = best_config.get("lora")

    data["_improve_loop_result"] = {
        "best_config_id":   best_config["id"],
        "bg_remove":        best_config["bg_remove"],
        "bg_model":         best_config.get("bg_model"),
        "lora_id":          lora["id"] if lora else None,
        "lora_trigger":     lora.get("trigger_word") if lora else None,
        "prompt_strategy":  ps.get("name"),
        "composite_avg":    best_config["scores"]["composite_avg"],
        "updated_at":       datetime.now(timezone.utc).isoformat(),
    }

    with open(PROMPTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  prompts.json を更新しました (最良設定: {best_config['id']})")


def save_config_snapshot(best_config: dict, iteration: int) -> None:
    """最良設定を configs/ にスナップショット保存する。"""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    snap = CONFIGS_DIR / f"best_iter{iteration:02d}_{ts}.json"
    CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(snap, "w", encoding="utf-8") as f:
        json.dump(best_config, f, ensure_ascii=False, indent=2)
    print(f"  設定スナップショット保存: {snap.name}")


def append_history(kb: dict, iteration: int, configs: list[dict]) -> None:
    """評価結果を knowledge_base.json の history に追記する。"""
    entry = {
        "iteration": iteration,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": [
            {
                "config_id":     c["id"],
                "composite_avg": c.get("scores", {}).get("composite_avg", 0),
            }
            for c in configs
        ],
    }
    kb.setdefault("evaluation_history", []).append(entry)
    research.save_knowledge_base(kb)


# ---------------------------------------------------------------------------
# メインループ
# ---------------------------------------------------------------------------

def run_loop(api: str, iterations: int, test_ids: list[str] | None,
             test_prompt: str | None, skip_research: bool) -> None:

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  LINEスタンプ 自動改善ループ")
    print("=" * 60)

    # Phase 1: Research
    if skip_research:
        print("\n[Phase 1] Research スキップ (--skip-research)")
        kb = research.load_knowledge_base()
    else:
        print("\n[Phase 1] Research — 外部情報収集")
        kb = research.run(report=False)

    for iteration in range(1, iterations + 1):
        print(f"\n{'─'*60}")
        print(f"  イテレーション {iteration}/{iterations}")
        print(f"{'─'*60}")

        # Phase 2: Configure
        print(f"\n[Phase 2] Configure — 実験設定を構築")
        configs = build_experiment_configs(kb, api)
        print(f"  生成設定数: {len(configs)}")
        for c in configs:
            lora_name = c["lora"]["id"].split("/")[-1] if c.get("lora") else "no-lora"
            print(f"  - {c['id']}")

        # Phase 3: Generate + Phase 4: Evaluate
        print(f"\n[Phase 3+4] Generate & Evaluate")
        for i, config in enumerate(configs, 1):
            print(f"\n  [{i}/{len(configs)}] {config['id']}")
            run_dir = run_generation(config, test_ids)
            config["scores"] = evaluate_run(run_dir, test_prompt)
            avg = config["scores"]["composite_avg"]
            print(f"  → composite_avg: {avg:.3f}")

        # Phase 5: Select & Update
        print(f"\n[Phase 5] Select — 最良設定を選択")
        best = select_best_config(configs)
        if best:
            print(f"  最良設定: {best['id']}")
            print(f"  スコア  : {best['scores']['composite_avg']:.3f}")
            update_prompts_with_best(best)
            save_config_snapshot(best, iteration)
        else:
            print("  [WARN] スコアが取得できた設定がありません。設定を確認してください。")

        append_history(kb, iteration, configs)
        print(f"\n  イテレーション {iteration} 完了")

    print(f"\n{'='*60}")
    print("  改善ループ完了")
    if best:
        print(f"  最終最良設定: {best['id']}")
        print(f"  最終スコア  : {best['scores']['composite_avg']:.3f}")
    print(f"  結果は {RESULTS_DIR} に保存されています")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="LINEスタンプ 自動改善ループ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--api", choices=["huggingface", "local", "gemini", "openai"],
                        default="huggingface",
                        help="画像生成API (デフォルト: huggingface)")
    parser.add_argument("--iterations", type=int, default=3,
                        help="改善ループの反復回数 (デフォルト: 3)")
    parser.add_argument("--test-id", nargs="*", default=None,
                        dest="test_ids",
                        help="評価に使うスタンプIDを絞り込む (例: 01_takubo_normal)")
    parser.add_argument("--test-prompt", default=None,
                        help="CLIPスコア算出用プロンプト (省略時はCLIPスキップ)")
    parser.add_argument("--research-only", action="store_true",
                        help="Phase 1 (Research) のみ実行して終了")
    parser.add_argument("--skip-research", action="store_true",
                        help="Phase 1 をスキップして既存の知識ベースを使用")
    args = parser.parse_args()

    if args.research_only:
        research.run(report=True)
        return

    run_loop(
        api=args.api,
        iterations=args.iterations,
        test_ids=args.test_ids,
        test_prompt=args.test_prompt,
        skip_research=args.skip_research,
    )


if __name__ == "__main__":
    main()
