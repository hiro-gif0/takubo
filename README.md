# OpenAI画像生成APIでチラシPNGを生成する

このリポジトリは **画像生成APIの実行を前提** にしています。  
SVGやHTML/CSSだけでチラシを再現する方式は使いません。

## 生成スクリプト

- `scripts/generate_flyer_with_openai.py`
- モデル名（コード内で明示）: `gpt-image-1`
- 出力先: `dist/flyer.png`

## 実行方法

```bash
export OPENAI_API_KEY="あなたのAPIキー"
python scripts/generate_flyer_with_openai.py
```

成功すると `dist/flyer.png` が生成されます。

## プレビュー

- `preview.html`
- `dist/preview.html`

上記ページは `dist/flyer.png` を表示します。

## 生成内容（プロンプトに含める要件）

- タイトル: ChatGPT Image 2.0 セミナー
- 日時: 2026年5月1日（金）20:00〜
- 会場: 静岡市駿河区 登呂3-1-1
- 講師: データサイエンティスト ヒロさん
- 内容: 初心者歓迎、画像生成の基本、実務活用、プロンプト設計
- 構図: A4縦に近い比率、視認性が高くイベント配布に使えるデザイン

## APIが使えない場合

スクリプトは以下を明示して終了します。

- `OPENAI_API_KEY` 未設定
- ネットワークエラー
- APIエラー（認証エラー・利用制限・不正なリクエストなど）
