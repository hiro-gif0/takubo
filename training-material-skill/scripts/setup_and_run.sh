#!/bin/bash
# Mac / Linux 用セットアップ＆実行スクリプト
# ターミナルで bash setup_and_run.sh を実行するだけでOK

echo "=== 必要ライブラリのインストール ==="
pip3 install python-pptx Pillow

echo ""
echo "=== 台本 → スライド画像 → PPTX（全工程） ==="
python3 run_all.py "$@"

echo ""
echo "output/training_material.pptx が生成されました。"
echo "Google スライドにアップロードするか、PowerPoint で開いてください。"
