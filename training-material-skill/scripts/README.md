# スライド自動生成スクリプト

`slide_script.md`（スライド台本）から **スライド画像の生成→PPTXの生成** を1コマンドで完結させます。
ChatGPT等の外部ツール不要。Python（Pillow + python-pptx）のみで動作します。

---

## スクリプト一覧

```
scripts/
├─ run_all.py                        ← 全工程オーケストレーター（これを実行する）
├─ generate_slides_from_script.py    ← 台本 → スライド画像生成
├─ slides_to_pptx.py                 ← スライド画像 → PPTX変換
├─ setup_and_run.sh                  ← Mac/Linux 用（初回セットアップ＋実行）
└─ setup_and_run.bat                 ← Windows 用（初回セットアップ＋実行）
```

---

## 使い方

### 前提：フォルダ構成

```
[作業フォルダ]/              例：examples/260527_独自ダネ研修/
├─ script/
│  └─ slide_script.md       ← 事前にClaudeと作る台本（必須）
├─ slides/                  ← 画像が自動生成される
└─ output/
   └─ training_material.pptx ← PPTXが自動生成される
```

### 手順1：初回セットアップ（1回のみ）

**Mac / Linux：**
```bash
pip3 install python-pptx Pillow
```

**Windows：**
```cmd
pip install python-pptx Pillow
```

### 手順2：台本を用意する

ClaudeにPrompt02（`prompts/02_slide_script_generation.md`）を使って台本を作成し、
`script/slide_script.md` として保存する。

### 手順3：1コマンドで実行

**Mac / Linux：**
```bash
python3 scripts/run_all.py examples/260527_独自ダネ研修
```

**Windows：**
```cmd
python scripts\run_all.py examples\260527_独自ダネ研修
```

### 手順4：Googleスライドへアップロード

`output/training_material.pptx` を Google ドライブにドラッグ＆ドロップ →
右クリック →「Google スライドで開く」

---

## トラブルシューティング

| エラーメッセージ | 対処 |
|---|---|
| `ModuleNotFoundError: No module named 'pptx'` | `pip3 install python-pptx` を実行する |
| `ModuleNotFoundError: No module named 'PIL'` | `pip3 install Pillow` を実行する |
| `エラー：台本ファイルが見つかりません` | `script/slide_script.md` が存在するか確認する |
| スライドの枚数がおかしい | `run_all.py` は毎回slidesフォルダをクリアするので再実行すればOK |
| 日本語が表示されない | IPAゴシック等の日本語フォントをインストールする（Mac/Linuxのみ） |
