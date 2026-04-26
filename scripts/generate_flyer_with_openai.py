#!/usr/bin/env python3
"""OpenAI画像生成APIを使って、A4縦チラシPNGを生成するスクリプト。"""

from __future__ import annotations

import base64
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

API_URL = "https://api.openai.com/v1/images/generations"
MODEL = "gpt-image-1"  # OpenAI 画像生成モデル名を明示
OUTPUT_PATH = pathlib.Path("dist/flyer.png")

PROMPT = """
A4縦に近い構図（印刷向け・高視認性）の日本語イベントチラシを作成してください。
デザイン要件:
- 実際のイベント配布に使える読みやすいレイアウト
- タイトルを最も目立たせる
- 情報を見出し付きカードで整理
- 余白を十分に取り、文字を潰さない
- モダンで信頼感のある配色（ネイビー＋アクセント）

必須記載内容:
- タイトル: ChatGPT Image 2.0 セミナー
- 日時: 2026年5月1日（金）20:00〜
- 会場: 静岡市駿河区 登呂3-1-1
- 講師: データサイエンティスト ヒロさん
- 内容: 初心者歓迎、画像生成の基本、実務活用、プロンプト設計

出力は1枚。日本語テキストの可読性を高く保ってください。
""".strip()


def main() -> int:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY が未設定です。", file=sys.stderr)
        print("理由: 画像生成APIを呼び出す認証情報がないため実行できません。", file=sys.stderr)
        return 2

    payload = {
        "model": MODEL,
        "prompt": PROMPT,
        "size": "1024x1536",
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        print(f"ERROR: API呼び出し失敗 HTTP {e.code}", file=sys.stderr)
        print(detail, file=sys.stderr)
        return 3
    except urllib.error.URLError as e:
        print("ERROR: ネットワークエラーでAPIに接続できませんでした。", file=sys.stderr)
        print(f"理由: {e}", file=sys.stderr)
        return 4

    try:
        parsed = json.loads(body)
        b64 = parsed["data"][0]["b64_json"]
    except Exception as e:  # noqa: BLE001
        print("ERROR: APIレスポンスの解析に失敗しました。", file=sys.stderr)
        print(f"理由: {e}", file=sys.stderr)
        print(body, file=sys.stderr)
        return 5

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(base64.b64decode(b64))
    print(f"OK: 画像を保存しました -> {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
