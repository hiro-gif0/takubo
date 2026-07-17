#!/usr/bin/env python3
"""
run_all.py — 全工程を1コマンドで実行するオーケストレーター

使い方：
  python3 run_all.py                              # カレントディレクトリで実行
  python3 run_all.py path/to/260527_独自ダネ研修  # 作業フォルダを指定

フォルダ構成（自動作成）：
  [作業フォルダ]/
  ├─ script/slide_script.md   ← 事前に用意する
  ├─ slides/                  ← 画像が自動生成される
  └─ output/                  ← PPTXが自動生成される
"""

import os
import sys
import subprocess
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent


def run(cmd: list[str], label: str):
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"\nエラー：{label} が失敗しました。")
        sys.exit(result.returncode)


def main():
    # 作業フォルダの決定
    work_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()

    script_path = work_dir / "script" / "slide_script.md"
    slides_dir  = work_dir / "slides"
    output_dir  = work_dir / "output"
    pptx_path   = output_dir / "training_material.pptx"

    print(f"作業フォルダ：{work_dir}")
    print(f"台本ファイル：{script_path}")

    # 台本ファイルの確認
    if not script_path.exists():
        print(f"\nエラー：台本ファイルが見つかりません")
        print(f"  → {script_path}")
        print(f"\n先に slide_script.md を作成してください。")
        print(f"  テンプレート：training-material-skill/templates/slide_structure_10枚.md")
        sys.exit(1)

    # 前回の画像をクリア（枚数ずれ防止）
    if slides_dir.exists():
        for f in slides_dir.glob("slide_*.png"):
            f.unlink()
    os.makedirs(slides_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # 工程6：スライド画像生成
    run(
        [sys.executable, str(SCRIPTS_DIR / "generate_slides_from_script.py"),
         str(script_path), str(slides_dir)],
        "工程6：slide_script.md → スライド画像生成"
    )

    # 工程7：PPTX変換
    run(
        [sys.executable, str(SCRIPTS_DIR / "slides_to_pptx.py"),
         str(slides_dir), str(pptx_path)],
        "工程7：スライド画像 → PPTX変換"
    )

    print(f"\n{'='*50}")
    print(f"  完了！")
    print(f"{'='*50}")
    print(f"\n出力ファイル：{pptx_path}")
    print(f"\n次のステップ：")
    print(f"  Google スライドにアップロード → ドライブにドラッグ＆ドロップ")
    print(f"  PowerPoint で開く            → .pptx をダブルクリック")


if __name__ == "__main__":
    main()
