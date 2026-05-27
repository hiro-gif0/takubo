# プロンプト05：PDF化・最終チェック

## 用途

工程7（PDF化・完了確認）を実行するプロンプト。
画像ファイルが揃った後の最終工程。

---

## PDF化の手順

### ステップ1：ファイル名の確認・連番化

全スライド画像ファイルを以下の命名規則で整理する。

```
slide_01.png
slide_02.png
slide_03.png
...
slide_10.png
```

ファイル名に日本語・スペースが含まれる場合は置換する。

### ステップ2：スライド順の確認

| ファイル名 | タイトル | 確認 |
|---|---|---|
| slide_01.png | 表紙 | □ |
| slide_02.png | この教材の目的 | □ |
| slide_03.png | 全体像 | □ |
| slide_04.png | メソッド1 | □ |
| slide_05.png | メソッド2 | □ |
| slide_06.png | メソッド3 | □ |
| slide_07.png | メソッド4 | □ |
| slide_08.png | メソッド5 | □ |
| slide_09.png | メソッド6 | □ |
| slide_10.png | まとめ | □ |

### ステップ3：画像→PDF変換コマンド

Pythonを使う場合：

```python
from PIL import Image
import os

slide_dir = "./slides"
output_pdf = "./output/training_material.pdf"

images = []
for i in range(1, 11):
    path = os.path.join(slide_dir, f"slide_{i:02d}.png")
    img = Image.open(path).convert("RGB")
    images.append(img)

images[0].save(
    output_pdf,
    save_all=True,
    append_images=images[1:]
)
print(f"PDF saved: {output_pdf}")
```

ImageMagickを使う場合：

```bash
convert slide_01.png slide_02.png slide_03.png ... slide_10.png output/training_material.pdf
```

### ステップ4：PDFリンクの提示

Claude Code sandbox上でのリンク提示形式：

```
[training_material.pdf をダウンロード](sandbox:/path/to/output/training_material.pdf)
```

**必ずクリック可能なリンク形式で提示する。テキストのみのファイルパス提示は禁止。**

---

## 最終完了チェックリスト

```
【教材情報】
- [ ] 発言者・日時・テーマが整理されている
- [ ] 教材コンセプト（3語の柱）が明確

【スライド品質】
- [ ] スライドが1枚1メッセージになっている
- [ ] 実例カードがある
- [ ] 注意点が注意ボックスに分離されている
- [ ] 「原文」「内部処理」などの制作側の言葉が含まれていない

【ファクトチェック】
- [ ] 人名表記が統一されている
- [ ] 肩書・日付・数字・固有名詞・引用が確認済み
- [ ] 原文にない断定がない

【ファイル】
- [ ] 1画像＝1スライドで生成されている
- [ ] ファイル名が連番化されている
- [ ] PDFとしてダウンロードできる（sandboxリンク）

【記録】
- [ ] 改善ログが更新されている
```

---

## 完了時の出力形式

```
## 教材化完了レポート

**教材タイトル：**
**対象：**
**スライド枚数：**
**ファクトチェック：** 完了 / 要確認事項あり（詳細は下記）

**ダウンロード：**
[training_material.pdf](sandbox:/output/training_material.pdf)

**要確認事項（あれば）：**
（残課題を列挙）

**改善ログ：**
（今回の作業で発見した問題と対策を記載）
```
