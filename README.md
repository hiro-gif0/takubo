# ChatGPT image2.0 セミナー チラシ（A4縦）

このリポジトリには、**A4縦の案内チラシ画像（SVG）**と、初心者向けのプレビュー導線を入れています。

## まず見るファイル（初心者向け）

1. `preview.html` をダブルクリックして開く
2. 画面内にチラシ画像がそのまま表示される

> これがいちばん簡単な「画像の見方」です。

## 生成物（dist/）

- `dist/chatgpt_image2_seminar_flyer_a4.svg`（配布元データ / 画像ファイル）
- `dist/preview.html`（ブラウザ確認用）
- `dist/chatgpt_image2_seminar_flyer_a4.png`（生成できた場合）
- `dist/chatgpt_image2_seminar_flyer_a4.pdf`（生成できた場合）

---

## 画像の見方（ローカルPC）

### 方法A（推奨）: preview.htmlで見る
1. `preview.html` をダブルクリック
2. ブラウザが開き、チラシ画像が表示されます

### 方法B: SVGを直接見る
1. `chatgpt_image2_seminar_flyer_a4.svg` をブラウザにドラッグ＆ドロップ
2. 拡大して文字の見え方を確認できます

---

## GitHub上で画像として確認する方法

PRを開いたあと、以下の順でクリックしてください。

1. **Files changed** タブを開く
2. `chatgpt_image2_seminar_flyer_a4.svg` をクリック
3. 右上またはファイル上部の **View file**（または **Raw**）をクリック
4. ブラウザでSVGが画像として表示されます

`dist/` 側を見たい場合は、
- `dist/chatgpt_image2_seminar_flyer_a4.svg`
- `dist/preview.html`
をクリックしてください。

---

## 印刷方法（A4縦）

1. `preview.html` または `chatgpt_image2_seminar_flyer_a4.svg` をブラウザで開く
2. `Ctrl + P`（Macは `Cmd + P`）で印刷画面を開く
3. 以下を設定
   - 用紙サイズ: **A4**
   - 向き: **縦**
   - 拡大縮小: **100% / 実際のサイズ**
   - 余白: **なし**（プリンタが対応していない場合は「最小」）

---

## PNG / PDF の作り方（可能なら）

```bash
./scripts/export_assets.sh
```

### スクリプトの内容
- `inkscape` / `rsvg-convert` / `magick` / `cairosvg` を自動検出
- 利用可能な場合、以下を `dist/` に生成
  - `dist/chatgpt_image2_seminar_flyer_a4.png`
  - `dist/chatgpt_image2_seminar_flyer_a4.pdf`

### 生成できない場合
変換ツールが未インストールの環境では、警告を出して終了します。
その場合でも `preview.html` と `chatgpt_image2_seminar_flyer_a4.svg` で画像確認は可能です。
