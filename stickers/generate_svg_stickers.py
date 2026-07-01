#!/usr/bin/env python3
"""
generate_svg_stickers.py — SVGベクター画像でLINEスタンプPNGを生成

cairosvg を使いローカルで完全無料・無制限に生成する。
ちびキャラ（タクボ市長・市議会）を SVG パスで描画し PNG に変換。

使い方:
  python stickers/generate_svg_stickers.py
  python stickers/generate_svg_stickers.py --ids 01_takubo_normal
  python stickers/generate_svg_stickers.py --no-rembg   # 背景除去スキップ
"""

import argparse
import sys
from pathlib import Path

try:
    import cairosvg
except ImportError:
    sys.exit("ERROR: cairosvg が未インストールです。pip install cairosvg を実行してください。")

from PIL import Image
import io

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "ai_dist"

# ─────────────────────────────────────────────
# カラーパレット
# ─────────────────────────────────────────────
C = {
    "skin":       "#FFCF9E",
    "skin_s":     "#EBA870",   # 影
    "hair":       "#EFEFEF",
    "hair_s":     "#C8C8C8",
    "jacket":     "#F47D20",
    "jacket_s":   "#C55E0A",
    "skirt":      "#1C3557",
    "shoe":       "#2A1505",
    "white":      "#FFFFFF",
    "outline":    "#1A1206",
    "eye":        "#2B1D0E",
    "cheek":      "#FFB3A7",
    "teeth":      "#FEFEFE",
    "tear":       "#8EC8F0",
    "red":        "#E03020",
    "yellow":     "#FFE835",
    "council_j":  "#2B4B8A",   # 議会ジャケット
    "council_s":  "#1A2F5C",
    "council_tie":"#C0201A",
    "gray_suit":  "#5A6070",
    "sweat":      "#A0D8F0",
}
OL = C["outline"]
SW = 3   # outline stroke-width

# ─────────────────────────────────────────────
# SVG ヘルパー
# ─────────────────────────────────────────────

def svg_open(w=370, h=320) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        '<defs>\n'
        '  <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">'
        '    <feDropShadow dx="2" dy="3" stdDeviation="2" flood-color="#00000030"/>'
        '  </filter>\n'
        '</defs>\n'
    )

def svg_close() -> str:
    return "</svg>"

def ellipse(cx, cy, rx, ry, fill, stroke=OL, sw=SW, extra="") -> str:
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>\n')

def rect(x, y, w, h, fill, stroke=OL, sw=SW, rx=0, extra="") -> str:
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>\n')

def path(d, fill, stroke=OL, sw=SW, extra="") -> str:
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round" {extra}/>\n')

def circle(cx, cy, r, fill, stroke=OL, sw=SW) -> str:
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')

def text_svg(x, y, content, size=22, fill="#1A1206", bold=True) -> str:
    fw = "bold" if bold else "normal"
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{fw}" '
            f'font-family="sans-serif" fill="{fill}" text-anchor="middle">'
            f'{content}</text>\n')


# ─────────────────────────────────────────────
# タクボ市長 ちびパーツ  (中心 cx=185, 頭上 cy=30)
# ─────────────────────────────────────────────

def takubo_base(cx=185, head_top=28, emotion="normal") -> str:
    """タクボ市長の基本ちびボディを返す"""
    s = ""
    hy = head_top + 55   # 頭の中心Y

    # ── 白髪 (後ろ) ──
    s += ellipse(cx, hy - 8, 44, 48, C["hair_s"], sw=0)
    # 髪の毛アウトシルエット
    s += path(f"M {cx-42},{hy+5} Q {cx-48},{hy-50} {cx},{hy-60} Q {cx+48},{hy-50} {cx+42},{hy+5} Z",
              C["hair"], sw=SW)
    # 短いボブ部分
    s += path(f"M {cx-40},{hy+10} Q {cx-52},{hy+35} {cx-38},{hy+50}",
              "none", stroke=C["hair_s"], sw=4)
    s += path(f"M {cx+40},{hy+10} Q {cx+52},{hy+35} {cx+38},{hy+50}",
              "none", stroke=C["hair_s"], sw=4)

    # ── 顔 ──
    s += ellipse(cx, hy, 42, 50, C["skin"])

    # ── ほっぺ ──
    s += ellipse(cx - 28, hy + 12, 10, 7, C["cheek"], stroke="none", sw=0)
    s += ellipse(cx + 28, hy + 12, 10, 7, C["cheek"], stroke="none", sw=0)

    # ── 眉 ──
    if emotion == "angry":
        s += path(f"M {cx-22},{hy-18} L {cx-8},{hy-12}", "none", stroke=OL, sw=3.5)
        s += path(f"M {cx+22},{hy-18} L {cx+8},{hy-12}", "none", stroke=OL, sw=3.5)
    elif emotion == "sad":
        s += path(f"M {cx-22},{hy-12} Q {cx-15},{hy-18} {cx-8},{hy-14}", "none", stroke=OL, sw=3)
        s += path(f"M {cx+22},{hy-12} Q {cx+15},{hy-18} {cx+8},{hy-14}", "none", stroke=OL, sw=3)
    elif emotion == "smug":
        s += path(f"M {cx-22},{hy-15} Q {cx-15},{hy-20} {cx-8},{hy-16}", "none", stroke=OL, sw=3)
        s += path(f"M {cx+22},{hy-20} Q {cx+15},{hy-16} {cx+8},{hy-18}", "none", stroke=OL, sw=3)
    else:
        s += path(f"M {cx-22},{hy-16} Q {cx-15},{hy-20} {cx-8},{hy-16}", "none", stroke=OL, sw=3)
        s += path(f"M {cx+22},{hy-16} Q {cx+15},{hy-20} {cx+8},{hy-16}", "none", stroke=OL, sw=3)

    # ── 目 ──
    if emotion == "crying":
        # うるうる目
        s += ellipse(cx - 14, hy - 4, 9, 11, C["white"])
        s += ellipse(cx + 14, hy - 4, 9, 11, C["white"])
        s += circle(cx - 14, hy - 3, 6, C["eye"])
        s += circle(cx + 14, hy - 3, 6, C["eye"])
        s += circle(cx - 12, hy - 6, 2, C["white"], stroke="none")
        s += circle(cx + 12, hy - 6, 2, C["white"], stroke="none")
        # 涙
        s += path(f"M {cx-18},{hy+8} Q {cx-16},{hy+18} {cx-14},{hy+26}", "none",
                  stroke=C["tear"], sw=3)
        s += path(f"M {cx+18},{hy+8} Q {cx+16},{hy+18} {cx+14},{hy+26}", "none",
                  stroke=C["tear"], sw=3)
    elif emotion == "angry":
        # つり目
        s += path(f"M {cx-22},{hy-6} Q {cx-14},{hy-2} {cx-6},{hy-6} Q {cx-14},{hy+2} Z",
                  C["eye"], stroke=OL, sw=1.5)
        s += path(f"M {cx+22},{hy-6} Q {cx+14},{hy-2} {cx+6},{hy-6} Q {cx+14},{hy+2} Z",
                  C["eye"], stroke=OL, sw=1.5)
    elif emotion == "smug":
        # 半目
        s += ellipse(cx - 14, hy - 3, 9, 7, C["white"])
        s += ellipse(cx + 14, hy - 3, 9, 7, C["white"])
        s += ellipse(cx - 14, hy - 3, 6, 5, C["eye"])
        s += ellipse(cx + 14, hy - 3, 6, 5, C["eye"])
        # 上まぶた
        s += path(f"M {cx-23},{hy-3} Q {cx-14},{hy-10} {cx-5},{hy-3}", "none",
                  stroke=OL, sw=3)
        s += path(f"M {cx+23},{hy-3} Q {cx+14},{hy-10} {cx+5},{hy-3}", "none",
                  stroke=OL, sw=3)
    else:
        # 普通の丸い目
        s += circle(cx - 14, hy - 3, 9, C["white"])
        s += circle(cx + 14, hy - 3, 9, C["white"])
        s += circle(cx - 14, hy - 2, 6, C["eye"])
        s += circle(cx + 14, hy - 2, 6, C["eye"])
        s += circle(cx - 12, hy - 4, 2, C["white"], stroke="none")
        s += circle(cx + 12, hy - 4, 2, C["white"], stroke="none")

    # ── 口 ──
    mouth_y = hy + 22
    if emotion == "normal":
        s += path(f"M {cx-10},{mouth_y} Q {cx},{mouth_y+8} {cx+10},{mouth_y}",
                  "none", stroke=OL, sw=3)
    elif emotion == "happy" or emotion == "battle":
        s += path(f"M {cx-14},{mouth_y} Q {cx},{mouth_y+14} {cx+14},{mouth_y}",
                  C["white"])
        s += path(f"M {cx-14},{mouth_y} Q {cx},{mouth_y+14} {cx+14},{mouth_y}",
                  "none", stroke=OL, sw=3)
    elif emotion == "crying":
        s += path(f"M {cx-12},{mouth_y+6} Q {cx},{mouth_y} {cx+12},{mouth_y+6}",
                  "none", stroke=OL, sw=3)
    elif emotion == "angry":
        s += path(f"M {cx-14},{mouth_y+4} Q {cx},{mouth_y} {cx+14},{mouth_y+4}",
                  C["white"])
        s += path(f"M {cx-14},{mouth_y+4} Q {cx},{mouth_y} {cx+14},{mouth_y+4}",
                  "none", stroke=OL, sw=3)
    elif emotion == "smug":
        s += path(f"M {cx-8},{mouth_y+2} Q {cx+2},{mouth_y+10} {cx+14},{mouth_y}",
                  "none", stroke=OL, sw=3)
    elif emotion == "sad":
        s += path(f"M {cx-10},{mouth_y+5} Q {cx},{mouth_y-2} {cx+10},{mouth_y+5}",
                  "none", stroke=OL, sw=3)

    # ── 首 ──
    body_top = hy + 48
    s += rect(cx - 12, body_top - 4, 24, 14, C["skin"], rx=5)

    # ── 上着 (オレンジジャケット) ──
    bt = body_top + 8
    s += path(f"M {cx-48},{bt} Q {cx-50},{bt+65} {cx-42},{bt+75} L {cx+42},{bt+75} Q {cx+50},{bt+65} {cx+48},{bt} Z",
              C["jacket"])
    # 白いインナー
    s += path(f"M {cx-12},{bt} L {cx-16},{bt+50} L {cx},{bt+55} L {cx+16},{bt+50} L {cx+12},{bt} Z",
              C["white"], stroke=OL, sw=2)
    # ボタン
    for i in range(3):
        s += circle(cx, bt + 18 + i * 14, 3, C["jacket_s"], stroke=OL, sw=1.5)
    # ラペル
    s += path(f"M {cx-12},{bt} L {cx-20},{bt+30} L {cx},{bt+40} Z",
              C["jacket_s"], stroke="none")
    s += path(f"M {cx+12},{bt} L {cx+20},{bt+30} L {cx},{bt+40} Z",
              C["jacket_s"], stroke="none")

    # ── 腕 (左) ──
    s += path(f"M {cx-48},{bt+5} Q {cx-60},{bt+40} {cx-50},{bt+65} Q {cx-40},{bt+70} {cx-36},{bt+60} Q {cx-44},{bt+38} {cx-34},{bt+8} Z",
              C["jacket"])
    # 左手
    s += ellipse(cx - 52, bt + 68, 12, 10, C["skin"])

    # ── 腕 (右) ──
    s += path(f"M {cx+48},{bt+5} Q {cx+60},{bt+40} {cx+50},{bt+65} Q {cx+40},{bt+70} {cx+36},{bt+60} Q {cx+44},{bt+38} {cx+34},{bt+8} Z",
              C["jacket"])
    # 右手
    s += ellipse(cx + 52, bt + 68, 12, 10, C["skin"])

    # ── スカート ──
    sk_top = bt + 74
    s += path(f"M {cx-44},{sk_top} Q {cx-50},{sk_top+45} {cx-46},{sk_top+55} L {cx+46},{sk_top+55} Q {cx+50},{sk_top+45} {cx+44},{sk_top} Z",
              C["skirt"])

    # ── 脚 ──
    leg_top = sk_top + 52
    s += rect(cx - 30, leg_top, 22, 35, C["skin"], rx=4)
    s += rect(cx + 8, leg_top, 22, 35, C["skin"], rx=4)
    # 靴
    s += path(f"M {cx-34},{leg_top+32} Q {cx-28},{leg_top+48} {cx-10},{leg_top+48} Q {cx-6},{leg_top+42} {cx-8},{leg_top+32} Z",
              C["shoe"])
    s += path(f"M {cx+6},{leg_top+32} Q {cx+12},{leg_top+48} {cx+30},{leg_top+48} Q {cx+34},{leg_top+42} {cx+32},{leg_top+32} Z",
              C["shoe"])

    return s


def takubo_fist_raised(cx=185, head_top=28) -> str:
    """右手を突き上げたポーズ (ガッツ)"""
    s = takubo_base(cx, head_top, emotion="happy")
    hy = head_top + 55
    bt = hy + 48 + 8

    # 右腕を上に変更（上書き効果のため少し調整）
    s += path(f"M {cx+48},{bt+5} Q {cx+65},{bt-20} {cx+58},{bt-50} Q {cx+44},{bt-58} {cx+38},{bt-46} Q {cx+46},{bt-22} {cx+34},{bt+8} Z",
              C["jacket"])
    s += ellipse(cx + 58, bt - 54, 12, 12, C["skin"])
    # こぶし
    s += rect(cx + 50, bt - 68, 18, 16, C["skin"], rx=5)

    # エネルギーライン
    for i, (dx, dy) in enumerate([(-12, -20), (5, -30), (20, -15)]):
        s += path(f"M {cx+58+dx},{bt-54+dy} L {cx+58+dx+8},{bt-54+dy-12}",
                  "none", stroke=C["yellow"], sw=3)

    return s


def takubo_angry_pose(cx=185, head_top=28) -> str:
    """怒り — 腕を広げて叫ぶ"""
    s = takubo_base(cx, head_top, emotion="angry")
    hy = head_top + 55
    bt = hy + 48 + 8

    # 怒りマーク
    s += text_svg(cx + 38, hy - 28, "💢", size=22, fill=C["red"], bold=False)
    # 両腕広げ (右)
    s += path(f"M {cx+48},{bt+5} Q {cx+72},{bt+10} {cx+78},{bt+28} Q {cx+66},{bt+34} {cx+58},{bt+24} Q {cx+54},{bt+12} {cx+34},{bt+8} Z",
              C["jacket"])
    s += ellipse(cx + 82, bt + 30, 12, 10, C["skin"])
    # 左腕
    s += path(f"M {cx-48},{bt+5} Q {cx-72},{bt+10} {cx-78},{bt+28} Q {cx-66},{bt+34} {cx-58},{bt+24} Q {cx-54},{bt+12} {cx-34},{bt+8} Z",
              C["jacket"])
    s += ellipse(cx - 82, bt + 30, 12, 10, C["skin"])

    return s


def takubo_crying_pose(cx=185, head_top=28) -> str:
    s = takubo_base(cx, head_top, emotion="crying")
    hy = head_top + 55
    bt = hy + 48 + 8
    # ハンカチ
    s += path(f"M {cx-52},{bt+58} Q {cx-58},{bt+70} {cx-44},{bt+72} Q {cx-30},{bt+70} {cx-32},{bt+58} Z",
              C["white"])
    s += ellipse(cx - 52, bt + 55, 14, 8, C["white"])
    return s


def takubo_battle_pose(cx=185, head_top=28) -> str:
    s = takubo_base(cx, head_top, emotion="battle")
    hy = head_top + 55
    bt = hy + 48 + 8

    # 右腕を前に突き出す
    s += path(f"M {cx+48},{bt+5} Q {cx+68},{bt+18} {cx+75},{bt+38} Q {cx+62},{bt+46} {cx+56},{bt+36} Q {cx+50},{bt+22} {cx+34},{bt+8} Z",
              C["jacket"])
    s += ellipse(cx + 78, bt + 42, 14, 11, C["skin"])
    # 構え効果
    for angle, length in [(-40, 20), (-25, 25), (-10, 22)]:
        import math
        rad = math.radians(angle)
        ex = cx + 78 + int(length * math.cos(rad))
        ey = bt + 42 + int(length * math.sin(rad))
        s += f'<line x1="{cx+78}" y1="{bt+42}" x2="{ex}" y2="{ey}" stroke="{C["yellow"]}" stroke-width="3" stroke-linecap="round"/>\n'

    return s


# ─────────────────────────────────────────────
# 市議会キャラ (スーツ、男性)
# ─────────────────────────────────────────────

def council_base(cx=185, head_top=28, emotion="normal") -> str:
    s = ""
    hy = head_top + 55

    # 黒髪
    s += ellipse(cx, hy - 8, 44, 48, "#2A2520", sw=0)
    s += path(f"M {cx-42},{hy+5} Q {cx-48},{hy-50} {cx},{hy-62} Q {cx+48},{hy-50} {cx+42},{hy+5} Z",
              "#2A2520", sw=SW)
    # 頭
    s += ellipse(cx, hy, 42, 50, C["skin"])
    s += ellipse(cx - 28, hy + 12, 10, 7, C["cheek"], stroke="none", sw=0)
    s += ellipse(cx + 28, hy + 12, 10, 7, C["cheek"], stroke="none", sw=0)

    # 眉
    if emotion == "smug":
        s += path(f"M {cx-22},{hy-20} Q {cx-15},{hy-16} {cx-8},{hy-18}", "none", stroke=OL, sw=3)
        s += path(f"M {cx+22},{hy-20} Q {cx+15},{hy-24} {cx+8},{hy-20}", "none", stroke=OL, sw=3)
    elif emotion == "angry":
        s += path(f"M {cx-22},{hy-18} L {cx-8},{hy-12}", "none", stroke=OL, sw=3.5)
        s += path(f"M {cx+22},{hy-18} L {cx+8},{hy-12}", "none", stroke=OL, sw=3.5)
    else:
        s += path(f"M {cx-22},{hy-16} Q {cx-15},{hy-20} {cx-8},{hy-16}", "none", stroke=OL, sw=3)
        s += path(f"M {cx+22},{hy-16} Q {cx+15},{hy-20} {cx+8},{hy-16}", "none", stroke=OL, sw=3)

    # 目
    if emotion == "smug":
        s += ellipse(cx - 14, hy - 3, 9, 7, C["white"])
        s += ellipse(cx + 14, hy - 3, 9, 7, C["white"])
        s += ellipse(cx - 16, hy - 3, 5, 5, C["eye"])
        s += ellipse(cx + 16, hy - 3, 5, 5, C["eye"])
        s += path(f"M {cx-23},{hy-3} Q {cx-14},{hy-10} {cx-5},{hy-3}", "none", stroke=OL, sw=3)
        s += path(f"M {cx+23},{hy-3} Q {cx+14},{hy-10} {cx+5},{hy-3}", "none", stroke=OL, sw=3)
    else:
        s += circle(cx - 14, hy - 3, 9, C["white"])
        s += circle(cx + 14, hy - 3, 9, C["white"])
        s += circle(cx - 14, hy - 2, 6, C["eye"])
        s += circle(cx + 14, hy - 2, 6, C["eye"])
        s += circle(cx - 12, hy - 4, 2, C["white"], stroke="none")
        s += circle(cx + 12, hy - 4, 2, C["white"], stroke="none")

    # 口
    mouth_y = hy + 22
    if emotion == "smug":
        s += path(f"M {cx-8},{mouth_y+2} Q {cx+2},{mouth_y+10} {cx+14},{mouth_y}",
                  "none", stroke=OL, sw=3)
    elif emotion == "angry":
        s += path(f"M {cx-14},{mouth_y+4} Q {cx},{mouth_y} {cx+14},{mouth_y+4}",
                  C["white"])
        s += path(f"M {cx-14},{mouth_y+4} Q {cx},{mouth_y} {cx+14},{mouth_y+4}",
                  "none", stroke=OL, sw=3)
    else:
        s += path(f"M {cx-10},{mouth_y} Q {cx},{mouth_y+8} {cx+10},{mouth_y}",
                  "none", stroke=OL, sw=3)

    # 首
    body_top = hy + 48
    s += rect(cx - 12, body_top - 4, 24, 14, C["skin"], rx=5)

    # スーツ
    bt = body_top + 8
    s += path(f"M {cx-48},{bt} Q {cx-50},{bt+65} {cx-42},{bt+75} L {cx+42},{bt+75} Q {cx+50},{bt+65} {cx+48},{bt} Z",
              C["council_j"])
    # 白シャツ
    s += path(f"M {cx-10},{bt} L {cx-14},{bt+50} L {cx},{bt+55} L {cx+14},{bt+50} L {cx+10},{bt} Z",
              C["white"], stroke=OL, sw=2)
    # ネクタイ
    s += path(f"M {cx-5},{bt+5} L {cx+5},{bt+5} L {cx+3},{bt+45} L {cx},{bt+52} L {cx-3},{bt+45} Z",
              C["council_tie"])
    # 腕
    s += path(f"M {cx-48},{bt+5} Q {cx-60},{bt+40} {cx-50},{bt+65} Q {cx-40},{bt+70} {cx-36},{bt+60} Q {cx-44},{bt+38} {cx-34},{bt+8} Z",
              C["council_j"])
    s += ellipse(cx - 52, bt + 68, 12, 10, C["skin"])
    s += path(f"M {cx+48},{bt+5} Q {cx+60},{bt+40} {cx+50},{bt+65} Q {cx+40},{bt+70} {cx+36},{bt+60} Q {cx+44},{bt+38} {cx+34},{bt+8} Z",
              C["council_j"])
    s += ellipse(cx + 52, bt + 68, 12, 10, C["skin"])

    # ズボン
    sk_top = bt + 74
    s += path(f"M {cx-44},{sk_top} Q {cx-50},{sk_top+45} {cx-46},{sk_top+55} L {cx+46},{sk_top+55} Q {cx+50},{sk_top+45} {cx+44},{sk_top} Z",
              C["council_s"])

    # 脚・靴
    leg_top = sk_top + 52
    s += rect(cx - 30, leg_top, 22, 35, C["council_s"], rx=4)
    s += rect(cx + 8, leg_top, 22, 35, C["council_s"], rx=4)
    s += path(f"M {cx-34},{leg_top+32} Q {cx-28},{leg_top+48} {cx-10},{leg_top+48} Q {cx-6},{leg_top+42} {cx-8},{leg_top+32} Z",
              C["shoe"])
    s += path(f"M {cx+6},{leg_top+32} Q {cx+12},{leg_top+48} {cx+30},{leg_top+48} Q {cx+34},{leg_top+42} {cx+32},{leg_top+32} Z",
              C["shoe"])

    return s


# ─────────────────────────────────────────────
# 対決シーン (2キャラ)
# ─────────────────────────────────────────────

def takubo_vs_council() -> str:
    s = svg_open()
    # 背景エフェクト
    s += path("M 185,160 L 0,0 L 370,0 Z", "#FFF9E0", stroke="none")
    s += path("M 185,160 L 370,320 L 0,320 Z", "#F0F0FF", stroke="none")

    # 放射線
    import math
    for i in range(12):
        angle = i * 30
        rad = math.radians(angle)
        x2 = 185 + 300 * math.cos(rad)
        y2 = 155 + 300 * math.sin(rad)
        col = C["yellow"] if i % 2 == 0 else "#FFF0A0"
        s += f'<line x1="185" y1="155" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{col}" stroke-width="12" opacity="0.4"/>\n'

    # タクボ (左)
    s += takubo_battle_pose(cx=100, head_top=20)
    # 議会 (右、ミラー)
    s += f'<g transform="translate(370,0) scale(-1,1)">\n'
    s += council_base(cx=100, head_top=20, emotion="angry")
    s += "</g>\n"

    # VS テキスト
    s += circle(185, 160, 30, C["red"])
    s += text_svg(185, 168, "VS", size=26, fill=C["white"])

    s += svg_close()
    return s


def takubo_smug_only() -> str:
    """議会が一人でニヤリ"""
    s = svg_open()
    s += council_base(cx=185, head_top=28, emotion="smug")
    # ニヤリ吹き出し
    s += path("M 240,60 Q 260,40 280,50 Q 290,30 310,40 Q 320,55 305,68 Q 285,75 260,70 Z",
              C["yellow"])
    s += text_svg(285, 62, "ふっ", size=18, fill=OL)
    s += svg_close()
    return s


def council_angry_only() -> str:
    """議会が不信任動議"""
    s = svg_open()
    s += council_base(cx=185, head_top=28, emotion="angry")
    # 不信任状
    s += rect(50, 200, 100, 70, C["white"], rx=5)
    s += text_svg(100, 228, "不信任", size=17, fill=OL)
    s += text_svg(100, 250, "動議！", size=17, fill=C["red"])
    s += svg_close()
    return s


# ─────────────────────────────────────────────
# スタンプ定義
# ─────────────────────────────────────────────

def make_normal() -> str:
    s = svg_open()
    s += takubo_base(emotion="normal")
    s += svg_close()
    return s

def make_ganbare() -> str:
    s = svg_open()
    s += takubo_fist_raised()
    s += svg_close()
    return s

def make_angry() -> str:
    s = svg_open()
    s += takubo_angry_pose()
    s += svg_close()
    return s

def make_crying() -> str:
    s = svg_open()
    s += takubo_crying_pose()
    s += svg_close()
    return s

def make_battle() -> str:
    s = svg_open()
    s += takubo_battle_pose()
    s += svg_close()
    return s

def make_council_smug() -> str:
    return takubo_smug_only()

def make_council_angry() -> str:
    return council_angry_only()

def make_vs() -> str:
    return takubo_vs_council()

def make_main_cover() -> str:
    s = svg_open(240, 240)
    s += f'<rect width="240" height="240" fill="#FFF8E1" rx="20"/>\n'
    # キャラを小さく中央に
    s += f'<g transform="translate(-65,-20) scale(0.85,0.85)">\n'
    s += takubo_base(emotion="happy")
    s += "</g>\n"
    s += text_svg(120, 218, "タクボ市長", size=18, fill=C["jacket_s"])
    s += svg_close()
    return s

def make_tab_icon() -> str:
    s = svg_open(96, 74)
    s += f'<rect width="96" height="74" fill="#FFF8E1" rx="8"/>\n'
    s += f'<g transform="translate(-50,-5) scale(0.41,0.41)">\n'
    s += takubo_base(emotion="normal")
    s += "</g>\n"
    s += svg_close()
    return s


STICKERS = {
    "01_takubo_normal":       (make_normal,        (370, 320)),
    "02_takubo_victory":      (make_ganbare,        (370, 320)),
    "03_takubo_angry":        (make_angry,          (370, 320)),
    "04_takubo_sad":          (make_crying,         (370, 320)),
    "05_takubo_battle":       (make_battle,         (370, 320)),
    "06_council_smug":        (make_council_smug,   (370, 320)),
    "07_council_angry":       (make_council_angry,  (370, 320)),
    "08_takubo_vs_council":   (make_vs,             (370, 320)),
    "main_cover":             (make_main_cover,     (240, 240)),
    "tab_icon":               (make_tab_icon,       (96, 74)),
}


def svg_to_png(svg_str: str, w: int, h: int) -> bytes:
    return cairosvg.svg2png(
        bytestring=svg_str.encode("utf-8"),
        output_width=w,
        output_height=h,
    )


def main():
    parser = argparse.ArgumentParser(description="SVGベクターでLINEスタンプPNG生成")
    parser.add_argument("--ids", nargs="*", default=None,
                        help="生成するスタンプID（省略時は全件）")
    parser.add_argument("--svg-only", action="store_true",
                        help="SVGファイルのみ保存（PNG変換なし）")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    global OUTPUT_DIR
    if args.output_dir:
        OUTPUT_DIR = Path(args.output_dir)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    svg_dir = SCRIPT_DIR / "src"
    svg_dir.mkdir(parents=True, exist_ok=True)

    targets = args.ids or list(STICKERS.keys())
    print(f"=== SVGスタンプ生成 ({len(targets)} 枚) → {OUTPUT_DIR} ===\n")

    for sid in targets:
        if sid not in STICKERS:
            print(f"  [SKIP] 不明なID: {sid}")
            continue

        fn, (w, h) = STICKERS[sid]
        print(f"  {sid} ({w}x{h}) ...", end="", flush=True)

        svg_str = fn()

        # SVG 保存
        svg_path = svg_dir / f"{sid}.svg"
        svg_path.write_text(svg_str, encoding="utf-8")

        if not args.svg_only:
            # PNG 変換
            png_bytes = svg_to_png(svg_str, w, h)
            out_path = OUTPUT_DIR / f"{sid}.png"
            out_path.write_bytes(png_bytes)
            kb = len(png_bytes) / 1024
            warn = "  ⚠ 500KB超" if kb > 500 else ""
            print(f" OK  ({kb:.0f} KB){warn}")
        else:
            print(f" SVG保存: {svg_path.name}")

    print(f"\n完了 → {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
