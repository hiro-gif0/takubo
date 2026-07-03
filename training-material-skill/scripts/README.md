# スライド自動変換スクリプト

ChatGPTで生成したスライド画像（PNG/JPG）を、PowerPoint（.pptx）に自動変換します。
生成された .pptx は Google スライドにそのままアップロードできます。

---

## フォルダ構成

```
scripts/
├─ slides_to_pptx.py     ← メインスクリプト
├─ setup_and_run.sh      ← Mac/Linux 用（初回セットアップ＋実行）
├─ setup_and_run.bat     ← Windows 用（初回セットアップ＋実行）
├─ slides/               ← ここに画像を入れる（自分で作成）
│  ├─ slide_01.png
│  ├─ slide_02.png
│  └─ ...
└─ output/               ← ここに .pptx が生成される（自動作成）
   └─ training_material.pptx
```

---

## 使い方

### 手順1：画像を準備する

ChatGPT で生成したスライド画像を `slides/` フォルダに入れる。

ファイル名は以下の形式にする（アルファベット順で並ぶ名前ならOK）：

```
slide_01.png
slide_02.png
slide_03.png
...
slide_10.png
```

### 手順2：スクリプトを実行する

**Mac / Linux の場合：**

```bash
bash setup_and_run.sh
```

または初回以降は：

```bash
python3 slides_to_pptx.py
```

**Windows の場合：**

`setup_and_run.bat` をダブルクリック

または初回以降は：

```cmd
python slides_to_pptx.py
```

### 手順3：出力ファイルを確認する

`output/training_material.pptx` が生成される。

### 手順4：Google スライドにアップロードする

1. Google ドライブを開く
2. `training_material.pptx` をドラッグ＆ドロップ
3. ファイルを右クリック →「Google スライドで開く」

---

## オプション：フォルダ名・出力先を変える

```bash
# スライドフォルダと出力ファイルを指定する場合
python3 slides_to_pptx.py ./my_slides ./output/研修資料_0603.pptx
```

---

## トラブルシューティング

| エラーメッセージ | 対処 |
|---|---|
| `ModuleNotFoundError: No module named 'pptx'` | `pip3 install python-pptx` を実行する |
| `エラー：フォルダが見つかりません` | `slides/` フォルダを作成して画像を入れる |
| `エラー：画像が見つかりません` | 拡張子が `.png` / `.jpg` か確認する |
| PowerPointで開いたら画像がずれている | 画像サイズが1280×720px か確認する |
