#!/bin/bash
# Mac / Linux 用セットアップ＆実行スクリプト
# ターミナルで bash setup_and_run.sh を実行するだけでOK

echo "=== python-pptx インストール ==="
pip3 install python-pptx

echo ""
echo "=== スライド → PPTX 変換 ==="
python3 slides_to_pptx.py

echo ""
echo "output/training_material.pptx が生成されました。"
echo "Google スライドにアップロードするか、PowerPoint で開いてください。"
