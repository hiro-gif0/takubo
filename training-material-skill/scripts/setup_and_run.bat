@echo off
REM Windows 用セットアップ＆実行スクリプト
REM ダブルクリックするだけでOK

echo === python-pptx インストール ===
pip install python-pptx

echo.
echo === スライド → PPTX 変換 ===
python slides_to_pptx.py

echo.
echo output\training_material.pptx が生成されました。
echo Google スライドにアップロードするか、PowerPoint で開いてください。
pause
