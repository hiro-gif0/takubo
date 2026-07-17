#!/usr/bin/env python3
"""
generate_slides_from_script.py

slide_script.md を読み込み、スライド画像（PNG）を自動生成する。
ChatGPT等の外部ツール不要。Pillowのみで動作。

使い方：
  python3 generate_slides_from_script.py slide_script.md ./slides
  python3 generate_slides_from_script.py  # デフォルト：./script/slide_script.md → ./slides
"""

import os
import re
import sys
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── カラー定義 ──────────────────────────────────────────────
C = {
    "navy":        "#1A2B5F",
    "yellow":      "#FFD700",
    "green":       "#2E7D32",
    "red":         "#C62828",
    "gray":        "#757575",
    "white":       "#FFFFFF",
    "light":       "#F8F8F8",
    "black":       "#1A1A1A",
    "green_light": "#E8F5E9",
    "red_light":   "#FFEBEE",
    "yellow_light":"#FFFDE7",
}

W, H = 1280, 720
FONT_PATHS = [
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def find_font():
    for p in FONT_PATHS:
        if os.path.exists(p):
            return p
    return None


FONT_PATH = find_font()


def font(size):
    if FONT_PATH:
        try:
            return ImageFont.truetype(FONT_PATH, size)
        except Exception:
            pass
    return ImageFont.load_default()


# ── Markdown パーサー ────────────────────────────────────────

def parse_slide_script(md_text: str) -> list[dict]:
    """slide_script.md を解析してスライド情報のリストを返す"""
    slides = []
    # ## スライドNN で分割
    blocks = re.split(r"\n## スライド\d+\n", "\n" + md_text)
    blocks = [b.strip() for b in blocks if b.strip() and "**タイトル" in b]

    for block in blocks:
        slide = {
            "title":      "",
            "point":      "",
            "body":       [],
            "example":    "",
            "layout":     "箇条書きリスト",
            "warning":    "",
            "flow_steps": [],
        }

        # **タイトル：** と **ここがポイント：** を抽出
        for line in block.splitlines():
            m = re.match(r"\*\*タイトル[：:]\*\*\s*(.*)", line)
            if m:
                slide["title"] = m.group(1).strip()
            m = re.match(r"\*\*ここがポイント[：:]\*\*\s*(.*)", line)
            if m:
                slide["point"] = m.group(1).strip()

        # ### セクションを分割
        sections = re.split(r"\n### ", block)
        for sec in sections:
            sec = sec.strip()
            if sec.startswith("本文"):
                items = [
                    re.sub(r"^[-*・]\s*", "", l).strip()
                    for l in sec.splitlines()[1:]
                    if re.match(r"^[-*・]", l.strip())
                ]
                slide["body"] = items

            elif sec.startswith("実例カード"):
                lines = [l.strip() for l in sec.splitlines()[1:] if l.strip() and not l.strip().startswith("（")]
                slide["example"] = " ".join(lines)

            elif sec.startswith("図解形式"):
                raw = " ".join(l.strip() for l in sec.splitlines()[1:] if l.strip())
                slide["layout"] = raw
                # フロー図のステップを抽出 例：フロー図（A → B → C）
                m = re.search(r"[（(](.+?)[）)]", raw)
                if m:
                    steps = re.split(r"[→\->/]", m.group(1))
                    slide["flow_steps"] = [s.strip() for s in steps if s.strip()]

            elif sec.startswith("注意ボックス"):
                lines = [l.strip() for l in sec.splitlines()[1:] if l.strip() and not l.strip().startswith("（")]
                slide["warning"] = " ".join(lines)

        slides.append(slide)
    return slides


# ── 描画ヘルパー ─────────────────────────────────────────────

def wrap_text(text: str, max_chars: int) -> list[str]:
    """日本語テキストを max_chars 文字で折り返す"""
    lines = []
    while len(text) > max_chars:
        lines.append(text[:max_chars])
        text = text[max_chars:]
    if text:
        lines.append(text)
    return lines


def draw_header(d: ImageDraw, title: str, point: str):
    d.rectangle([0, 0, W, 110], fill=hex2rgb(C["navy"]))
    d.text((55, 18), title, font=font(38), fill=hex2rgb(C["white"]))
    if point:
        d.text((57, 72), point, font=font(21), fill=hex2rgb(C["yellow"]))


def draw_footer(d: ImageDraw, idx: int, total: int, meta: str):
    d.rectangle([0, H - 36, W, H], fill=hex2rgb(C["navy"]))
    d.text((55, H - 26), meta, font=font(16), fill=hex2rgb(C["yellow"]))
    d.text((W - 90, H - 26), f"{idx} / {total}", font=font(16), fill=hex2rgb(C["white"]))


def draw_bullets(d: ImageDraw, items: list[str], y: int, max_chars=38) -> int:
    f = font(22)
    for item in items:
        lines = wrap_text(item, max_chars)
        for i, line in enumerate(lines):
            prefix = "• " if i == 0 else "  "
            d.text((70, y), prefix + line, font=f, fill=hex2rgb(C["black"]))
            y += 38
        y += 6
    return y


def draw_flow(d: ImageDraw, steps: list[str], y: int):
    if not steps:
        return
    n = len(steps)
    box_w = min(220, (W - 120 - 30 * (n - 1)) // n)
    box_h = 70
    gap = 30
    total_w = box_w * n + gap * (n - 1)
    x0 = (W - total_w) // 2
    colors = [C["navy"], C["green"], C["navy"], C["green"], C["navy"]]
    f = font(19)
    for i, step in enumerate(steps):
        x = x0 + i * (box_w + gap)
        c = hex2rgb(colors[i % 2])
        d.rounded_rectangle([x, y, x + box_w, y + box_h], radius=10, fill=c)
        lines = wrap_text(step, 8)
        ty = y + (box_h - 24 * len(lines)) // 2
        for line in lines:
            tx = x + (box_w - len(line) * 12) // 2
            d.text((tx, ty), line, font=f, fill=hex2rgb(C["white"]))
            ty += 26
        if i < n - 1:
            ax = x + box_w + 4
            ay = y + box_h // 2
            d.polygon([(ax, ay - 7), (ax + 18, ay), (ax, ay + 7)],
                      fill=hex2rgb(C["gray"]))


def draw_example_card(d: ImageDraw, text: str, y: int) -> int:
    if not text:
        return y
    lines = wrap_text(text, 60)
    card_h = 36 + 28 * len(lines)
    d.rectangle([50, y, W - 50, y + card_h], fill=hex2rgb(C["green_light"]))
    d.rectangle([50, y, 58, y + card_h], fill=hex2rgb(C["green"]))
    d.text((68, y + 6), "実例", font=font(17), fill=hex2rgb(C["green"]))
    f = font(19)
    ty = y + 30
    for line in lines:
        d.text((68, ty), line, font=f, fill=hex2rgb(C["black"]))
        ty += 28
    return y + card_h + 12


def draw_warning_box(d: ImageDraw, text: str, y: int) -> int:
    if not text:
        return y
    lines = wrap_text(text, 58)
    box_h = 36 + 26 * len(lines)
    d.rectangle([50, y, W - 50, y + box_h], fill=hex2rgb(C["red_light"]))
    d.rectangle([50, y, 58, y + box_h], fill=hex2rgb(C["red"]))
    f = font(19)
    ty = y + 8
    for i, line in enumerate(lines):
        prefix = "！ " if i == 0 else "   "
        d.text((68, ty), prefix + line, font=f, fill=hex2rgb(C["red"]))
        ty += 26
    return y + box_h + 10


# ── スライドレンダラー ────────────────────────────────────────

def render_slide(slide: dict, idx: int, total: int, footer_meta: str) -> Image.Image:
    layout = slide["layout"]
    is_cover = (idx == 1) or "表紙" in layout

    # 表紙
    if is_cover:
        img = Image.new("RGB", (W, H), hex2rgb(C["navy"]))
        d = ImageDraw.Draw(img)
        d.rectangle([55, 120, W - 55, H - 55], fill=hex2rgb(C["white"]))
        d.text((100, 165), slide["title"], font=font(52), fill=hex2rgb(C["navy"]))
        d.rectangle([100, 242, 620, 246], fill=hex2rgb(C["yellow"]))
        if slide["point"]:
            d.text((100, 258), slide["point"], font=font(26), fill=hex2rgb(C["gray"]))
        y = 370
        for item in slide["body"]:
            d.text((100, y), item, font=font(20), fill=hex2rgb(C["gray"]))
            y += 38
        draw_footer(d, idx, total, footer_meta)
        return img

    img = Image.new("RGB", (W, H), hex2rgb(C["light"]))
    d = ImageDraw.Draw(img)
    draw_header(d, slide["title"], slide["point"])

    y = 132
    is_flow = "フロー" in layout
    has_example = bool(slide["example"])
    has_warning = bool(slide["warning"])

    # 本文
    if slide["body"]:
        body_end = H - 60
        if is_flow:
            body_end = 340
        elif has_example and has_warning:
            body_end = 380
        elif has_example or has_warning:
            body_end = 450
        y = draw_bullets(d, slide["body"], y)

    # フロー図
    if is_flow and slide["flow_steps"]:
        flow_y = y + 10 if y > 140 else 200
        flow_y = min(flow_y, 340)
        draw_flow(d, slide["flow_steps"], flow_y)
        y = flow_y + 100

    # 実例カード・注意ボックスの配置
    bottom_items = []
    if has_example:
        bottom_items.append(("example", slide["example"]))
    if has_warning:
        bottom_items.append(("warning", slide["warning"]))

    if bottom_items:
        # 下部に積む（最大2要素）
        if len(bottom_items) == 2:
            total_h = 100 + 80  # 概算
            start_y = H - 36 - total_h - 20
        else:
            start_y = H - 36 - 90 - 10

        cur_y = max(y + 20, start_y)
        for kind, text in bottom_items:
            if kind == "example":
                cur_y = draw_example_card(d, text, cur_y)
            else:
                cur_y = draw_warning_box(d, text, cur_y)

    draw_footer(d, idx, total, footer_meta)
    return img


# ── メイン ───────────────────────────────────────────────────

def main():
    script_path = sys.argv[1] if len(sys.argv) > 1 else "./script/slide_script.md"
    output_dir  = sys.argv[2] if len(sys.argv) > 2 else "./slides"

    if not os.path.exists(script_path):
        print(f"エラー：台本ファイルが見つかりません → {script_path}")
        sys.exit(1)

    md_text = Path(script_path).read_text(encoding="utf-8")

    # フッター用メタ情報を台本から抽出
    footer_meta = "社内限定資料"
    for line in md_text.splitlines():
        if "発言者" in line or "日時" in line:
            v = line.split("：", 1)[-1].strip()
            if "日時" in line:
                footer_meta = v + "　社内限定"
                break

    slides = parse_slide_script(md_text)
    if not slides:
        print("エラー：台本を解析できませんでした。フォーマットを確認してください。")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    total = len(slides)
    print(f"台本を読み込みました：{total} 枚")

    for i, slide in enumerate(slides, 1):
        img = render_slide(slide, i, total, footer_meta)
        out_path = os.path.join(output_dir, f"slide_{i:02d}.png")
        img.save(out_path)
        print(f"  [{i:02d}] {slide['title'][:30]} → {out_path}")

    print(f"\n完了：{output_dir}/ に {total} 枚を保存しました。")
    print("次のステップ：python3 slides_to_pptx.py を実行してPPTXを生成する")


if __name__ == "__main__":
    main()
