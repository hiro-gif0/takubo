# 取材勉強会・文字起こし教材化 Skill

新聞社内の勉強会・取材ノウハウ共有・講評・質疑応答の文字起こしを、若手記者向け社内教材へ変換するClaude Code Skill。

---

## 使い方（最短手順）

### 1. プロジェクトディレクトリで Claude Code を起動

```bash
cd training-material-skill
claude
```

### 2. 以下のプロンプトで呼び出す

```
取材勉強会の文字起こし教材化をお願いします。

【文字起こし】
（ここに文字起こしを貼る）

【発言者・肩書】
（例：田中記者・社会部）

【日時】
（例：2026年5月27日）

【公開範囲】
（例：社内限定）
```

---

## ディレクトリ構成

```
training-material-skill/
├─ README.md              ← このファイル
├─ SKILL.md               ← Skill仕様書（設計思想・ワークフロー）
├─ CLAUDE.md              ← Claudeへの動作指示
├─ prompts/
│  ├─ 01_transcript_to_teaching_material.md   ← 工程1〜3：分解・コンセプト化
│  ├─ 02_slide_script_generation.md           ← 工程4：台本作成
│  ├─ 03_gpt_image_slide_prompt.md            ← 工程6：画像生成プロンプト
│  ├─ 04_fact_check_prompt.md                 ← 工程5：ファクトチェック
│  └─ 05_pdf_export_checklist.md              ← 工程7：PDF化
├─ templates/
│  ├─ slide_structure_10枚.md                 ← 10枚構成テンプレート
│  ├─ fact_check_table.md                     ← ファクトチェック表
│  ├─ improvement_log.md                      ← 改善ログテンプレート
│  └─ visual_design_rules.md                  ← 視覚設計ルール
└─ examples/
   └─ 260527_独自ダネ研修/                     ← 実際の使用例
```

---

## ワークフロー概要

```
入力確認 → 文字起こし分解 → コンセプト化 → 台本作成 → ファクトチェック → スライド生成 → PDF化
```

各工程は独立したプロンプトファイルに対応しているため、途中から再開することも可能。

---

## 出力形式の選択

| 出力形式 | 内容 | 使うプロンプト |
|---|---|---|
| 分解のみ | 文字起こしを8カテゴリに整理 | 01 |
| 台本まで | スライド台本＋ファクトチェック表 | 01, 02, 04 |
| 画像まで | 台本＋GPT Image用プロンプト | 01, 02, 03, 04 |
| PDF完成 | 全工程 | 01〜05 |

---

## 改善ログ

`examples/[日付_テーマ]/improvement_log.md` に毎回記録する。
テンプレートは `templates/improvement_log.md` を使う。
