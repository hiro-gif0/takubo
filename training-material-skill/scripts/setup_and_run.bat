@echo off
REM Windows 用セットアップ＆実行スクリプト
REM ダブルクリックするだけでOK

echo === python-pptx インストール ===
pip install python-pptx

echo.
echo === 台本 → スライド画像 → PPTX（全工程） ===
python run_all.py %*

echo.
echo output\training_material.pptx が生成されました。
echo Google スライドにアップロードするか、PowerPoint で開いてください。
pause
