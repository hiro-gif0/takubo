#!/usr/bin/env python3
"""
generate_svg_stickers.py — 可愛いちびキャラLINEスタンプ生成

ちびキャラ比率 (頭2:体1) + 大きな目 + 丸みのあるフォルムで
「愛敬のある」スタンプを生成する。

使い方:
  python stickers/generate_svg_stickers.py
  python stickers/generate_svg_stickers.py --ids 01_takubo_normal
"""

import argparse, sys, math
from pathlib import Path

try:
    import cairosvg
except ImportError:
    sys.exit("pip install cairosvg")

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "ai_dist"
SVG_DIR    = SCRIPT_DIR / "src"

# ── パレット ──────────────────────────────────────────────
P = {
    "skin":     "#FFE0B8",
    "skin_s":   "#F5C08A",   # 影
    "hair":     "#F4F4F4",   # タクボ白髪
    "hair_s":   "#C8C8CE",
    "hair_hi":  "#FFFFFF",   # ハイライト
    "jacket":   "#F58220",   # オレンジジャケット
    "jacket_s": "#C86010",
    "collar":   "#FFF8F0",
    "skirt":    "#1D3461",
    "skirt_s":  "#0F1F3D",
    "shoe":     "#221408",
    "stocking": "#F5D0B0",
    "eye":      "#2B1D0E",
    "pupil_hi": "#FFFFFF",
    "cheek":    "#FFAAB0",   # ほっぺピンク
    "mouth":    "#E05060",
    "teeth":    "#FFFEF8",
    "glasses":  "#4A3010",
    "outline":  "#1A1206",
    # 市議会
    "c_suit":   "#213660",
    "c_suit_s": "#111E40",
    "c_hair":   "#1C1C1C",
    "c_tie":    "#C01818",
    "c_shirt":  "#FAFAFA",
    # エフェクト
    "yellow":   "#FFE535",
    "orange":   "#FF8C00",
    "red":      "#E82020",
    "blue":     "#3090D8",
    "star":     "#FFD700",
    "sweat":    "#90CCEE",
    "tear":     "#70B8E8",
    "heart":    "#FF6090",
    "speech":   "#FEFEF0",
}
OL = P["outline"]
SW = 3.5   # 基本アウトライン幅


# ── SVG プリミティブ ──────────────────────────────────────
def svg_open(w=370, h=320):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
    )

def svg_close():
    return "</svg>\n"

def g(content, transform=""):
    return f'<g transform="{transform}">\n{content}</g>\n'

def el(cx, cy, rx, ry, fill, stroke=OL, sw=SW, extra=""):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>\n')

def ci(cx, cy, r, fill, stroke=OL, sw=SW, extra=""):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>\n')

def rc(x, y, w, h, fill, stroke=OL, sw=SW, rx=0, extra=""):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>\n')

def pa(d, fill, stroke=OL, sw=SW, cap="round", join="round", extra=""):
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linecap="{cap}" stroke-linejoin="{join}" {extra}/>\n')

def li(x1, y1, x2, y2, stroke, sw=3, cap="round"):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}"/>\n')

def tx(x, y, txt, size=20, fill="#1A1206", bold=True, anchor="middle"):
    fw = "bold" if bold else "normal"
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{fw}" '
            f'font-family="\'Hiragino Maru Gothic Pro\', \'Rounded Mplus 1c\', sans-serif" '
            f'fill="{fill}" text-anchor="{anchor}">{txt}</text>\n')


# ── 星・ハート・エフェクトヘルパー ───────────────────────
def star_shape(cx, cy, r_out, r_in, pts, fill, stroke=OL, sw=1.5):
    coords = []
    for i in range(pts * 2):
        angle = math.radians(i * 180 / pts - 90)
        r = r_out if i % 2 == 0 else r_in
        coords.append(f"{cx + r*math.cos(angle):.1f},{cy + r*math.sin(angle):.1f}")
    d = "M " + " L ".join(coords) + " Z"
    return pa(d, fill, stroke, sw)

def heart(cx, cy, size, fill, stroke=OL, sw=2):
    s = size
    d = (f"M {cx},{cy+s*0.4} "
         f"C {cx},{cy-s*0.1} {cx-s},{cy-s*0.6} {cx-s},{cy-s*0.1} "
         f"C {cx-s},{cy-s*0.8} {cx},{cy-s*1.0} {cx},{cy-s*0.4} "
         f"C {cx},{cy-s*1.0} {cx+s},{cy-s*0.8} {cx+s},{cy-s*0.1} "
         f"C {cx+s},{cy-s*0.6} {cx},{cy-s*0.1} {cx},{cy+s*0.4} Z")
    return pa(d, fill, stroke, sw)

def speech_bubble(x, y, w, h, tail_x, tail_y, fill=P["speech"], stroke=OL, sw=SW):
    rx = h * 0.4
    s = rc(x, y, w, h, fill, stroke, sw, rx=rx)
    s += pa(f"M {tail_x-8},{tail_y-2} L {tail_x},{tail_y+14} L {tail_x+10},{tail_y-2} Z",
            fill, stroke, sw)
    return s


# ══════════════════════════════════════════════════════════
# タクボ市長 ちびキャラ
# 設計: cx=185 を中心, head_top=20 から描画
# 頭の半径: rx=68 ry=72 (大きくて丸い)
# 全体高: ~290px に収める
# ══════════════════════════════════════════════════════════

def _takubo_head(cx, hy, emotion="normal"):
    """顔・髪・眼鏡を描く"""
    s = ""

    # ── 白髪 (ボブ、後ろ側) ──────────────────────────────
    # 髪のベース (顔より後ろ)
    s += pa(
        f"M {cx-62},{hy+20} "
        f"Q {cx-72},{hy-30} {cx-50},{hy-72} "
        f"Q {cx-25},{hy-90} {cx},{hy-92} "
        f"Q {cx+25},{hy-90} {cx+50},{hy-72} "
        f"Q {cx+72},{hy-30} {cx+62},{hy+20} Z",
        P["hair"], OL, SW
    )
    # サイドの流れ (左右のボブが少し外に広がる)
    s += pa(
        f"M {cx-62},{hy+20} Q {cx-75},{hy+40} {cx-65},{hy+58} Q {cx-58},{hy+68} {cx-48},{hy+65}",
        "none", P["hair_s"], 4
    )
    s += pa(
        f"M {cx+62},{hy+20} Q {cx+75},{hy+40} {cx+65},{hy+58} Q {cx+58},{hy+68} {cx+48},{hy+65}",
        "none", P["hair_s"], 4
    )
    # ハイライト
    s += pa(
        f"M {cx-20},{hy-88} Q {cx},{hy-96} {cx+20},{hy-85}",
        "none", P["hair_hi"], 5
    )

    # ── 顔 ──────────────────────────────────────────────
    s += el(cx, hy, 60, 68, P["skin"])

    # ── ほっぺ (大きめ、透過気味) ──────────────────────
    s += el(cx-38, hy+18, 16, 10, P["cheek"],
            stroke="none", sw=0, extra='opacity="0.7"')
    s += el(cx+38, hy+18, 16, 10, P["cheek"],
            stroke="none", sw=0, extra='opacity="0.7"')

    # ── 眉 ──────────────────────────────────────────────
    if emotion == "angry":
        s += pa(f"M {cx-30},{hy-28} Q {cx-18},{hy-18} {cx-8},{hy-24}",
                "none", OL, 4)
        s += pa(f"M {cx+30},{hy-28} Q {cx+18},{hy-18} {cx+8},{hy-24}",
                "none", OL, 4)
    elif emotion == "sad":
        s += pa(f"M {cx-30},{hy-20} Q {cx-20},{hy-28} {cx-8},{hy-22}",
                "none", OL, 3.5)
        s += pa(f"M {cx+30},{hy-20} Q {cx+20},{hy-28} {cx+8},{hy-22}",
                "none", OL, 3.5)
    elif emotion in ("smug", "smug2"):
        s += pa(f"M {cx-30},{hy-24} Q {cx-20},{hy-30} {cx-8},{hy-25}",
                "none", OL, 3.5)
        s += pa(f"M {cx+30},{hy-32} Q {cx+20},{hy-24} {cx+8},{hy-28}",
                "none", OL, 4)
    else:
        s += pa(f"M {cx-30},{hy-25} Q {cx-20},{hy-32} {cx-8},{hy-26}",
                "none", OL, 3.5)
        s += pa(f"M {cx+30},{hy-25} Q {cx+20},{hy-32} {cx+8},{hy-26}",
                "none", OL, 3.5)

    # ── 目 (大きくてキラキラ) ───────────────────────────
    ex_l, ex_r = cx - 22, cx + 22
    ey = hy - 8

    if emotion == "crying":
        # うるうる大きな瞳
        s += el(ex_l, ey, 14, 16, P["skin_s"], stroke="none")  # まぶた影
        s += el(ex_r, ey, 14, 16, P["skin_s"], stroke="none")
        s += el(ex_l, ey+1, 13, 15, "#D8F0FF")
        s += el(ex_r, ey+1, 13, 15, "#D8F0FF")
        s += ci(ex_l, ey+2, 9, P["eye"])
        s += ci(ex_r, ey+2, 9, P["eye"])
        s += ci(ex_l-3, ey-4, 3, P["pupil_hi"], stroke="none")
        s += ci(ex_r-3, ey-4, 3, P["pupil_hi"], stroke="none")
        s += ci(ex_l+2, ey+3, 1.5, P["pupil_hi"], stroke="none")
        s += ci(ex_r+2, ey+3, 1.5, P["pupil_hi"], stroke="none")
        # まつ毛
        for dx in [-6, 0, 6]:
            s += li(ex_l+dx, ey-14, ex_l+dx-1, ey-20, OL, 2)
            s += li(ex_r+dx, ey-14, ex_r+dx+1, ey-20, OL, 2)
        # 涙
        s += pa(f"M {ex_l-6},{ey+14} Q {ex_l-8},{ey+30} {ex_l-4},{ey+44}",
                "none", P["tear"], 3.5)
        s += pa(f"M {ex_r+6},{ey+14} Q {ex_r+8},{ey+30} {ex_r+4},{ey+44}",
                "none", P["tear"], 3.5)
        # 涙のしずく
        s += el(ex_l-4, ey+48, 4, 6, P["tear"], stroke=P["blue"], sw=1)
        s += el(ex_r+4, ey+48, 4, 6, P["tear"], stroke=P["blue"], sw=1)

    elif emotion == "angry":
        # つり目
        s += pa(f"M {ex_l-14},{ey-4} Q {ex_l},{ey+6} {ex_l+12},{ey-2} "
                f"Q {ex_l},{ey+14} {ex_l-14},{ey+4} Z",
                P["eye"])
        s += pa(f"M {ex_r-12},{ey-2} Q {ex_r},{ey+6} {ex_r+14},{ey-4} "
                f"Q {ex_r+14},{ey+4} {ex_r},{ey+14} Z",
                P["eye"])
        s += ci(ex_l-2, ey+1, 2.5, P["pupil_hi"], stroke="none")
        s += ci(ex_r+2, ey+1, 2.5, P["pupil_hi"], stroke="none")
        # 怒りプチライン
        s += li(ex_l-14, ey-4, ex_l-22, ey-14, OL, 3)
        s += li(ex_r+14, ey-4, ex_r+22, ey-14, OL, 3)

    elif emotion in ("smug", "smug2"):
        # 半目ニヤリ
        s += el(ex_l, ey+2, 13, 11, "#D0F0E0")
        s += el(ex_r, ey+2, 13, 11, "#D0F0E0")
        s += ci(ex_l, ey+3, 8, P["eye"])
        s += ci(ex_r+2, ey+3, 8, P["eye"])
        # 上まぶた (半分隠す)
        s += pa(f"M {ex_l-14},{ey+2} Q {ex_l},{ey-10} {ex_l+14},{ey+2}",
                P["skin"], stroke="none")
        s += pa(f"M {ex_r-14},{ey+2} Q {ex_r},{ey-10} {ex_r+14},{ey+2}",
                P["skin"], stroke="none")
        s += pa(f"M {ex_l-14},{ey+2} Q {ex_l},{ey-10} {ex_l+14},{ey+2}",
                "none", OL, 3)
        s += pa(f"M {ex_r-14},{ey+2} Q {ex_r},{ey-10} {ex_r+14},{ey+2}",
                "none", OL, 3)
        s += ci(ex_l-3, ey-2, 2.5, P["pupil_hi"], stroke="none")
        s += ci(ex_r-1, ey-2, 2.5, P["pupil_hi"], stroke="none")

    else:
        # 通常の丸くて大きな目
        s += el(ex_l, ey, 14, 16, "#E8F5FF")
        s += el(ex_r, ey, 14, 16, "#E8F5FF")
        s += ci(ex_l, ey+1, 10, P["eye"])
        s += ci(ex_r, ey+1, 10, P["eye"])
        s += ci(ex_l-4, ey-4, 3.5, P["pupil_hi"], stroke="none")
        s += ci(ex_r-4, ey-4, 3.5, P["pupil_hi"], stroke="none")
        s += ci(ex_l+2, ey+3, 1.8, P["pupil_hi"], stroke="none")
        s += ci(ex_r+2, ey+3, 1.8, P["pupil_hi"], stroke="none")
        # まつ毛
        for dx in [-4, 4]:
            s += li(ex_l+dx, ey-15, ex_l+dx-1, ey-21, OL, 2)
            s += li(ex_r+dx, ey-15, ex_r+dx+1, ey-21, OL, 2)

    # 目のアウトライン
    if emotion not in ("angry",):
        s += el(ex_l, ey, 14, 16, "none", OL, SW)
        s += el(ex_r, ey, 14, 16, "none", OL, SW)

    # ── 鼻 (小さな丸) ──────────────────────────────────
    s += ci(cx, hy+8, 3, P["skin_s"], stroke="none")

    # ── 口 ──────────────────────────────────────────────
    my = hy + 32
    if emotion == "normal":
        s += pa(f"M {cx-12},{my} Q {cx},{my+10} {cx+12},{my}",
                "none", P["mouth"], 3.5)
    elif emotion in ("happy", "battle", "victory"):
        # 大きな笑顔
        s += pa(f"M {cx-18},{my-2} Q {cx},{my+22} {cx+18},{my-2}",
                P["teeth"])
        s += pa(f"M {cx-18},{my-2} Q {cx},{my+22} {cx+18},{my-2}",
                "none", P["mouth"], 3.5)
        # 舌 (ガッツのみ)
        if emotion == "victory":
            s += el(cx, my+14, 8, 6, "#FF8090", stroke=P["mouth"], sw=2)
    elif emotion == "crying":
        s += pa(f"M {cx-14},{my+8} Q {cx},{my-2} {cx+14},{my+8}",
                "none", P["mouth"], 3.5)
    elif emotion == "angry":
        s += pa(f"M {cx-16},{my+6} Q {cx},{my} {cx+16},{my+6}",
                P["teeth"])
        s += pa(f"M {cx-16},{my+6} Q {cx},{my} {cx+16},{my+6}",
                "none", P["mouth"], 3.5)
    elif emotion == "sad":
        s += pa(f"M {cx-12},{my+6} Q {cx},{my-4} {cx+12},{my+6}",
                "none", P["mouth"], 3.5)
    elif emotion in ("smug", "smug2"):
        s += pa(f"M {cx-4},{my+4} Q {cx+4},{my+14} {cx+16},{my+2}",
                "none", P["mouth"], 3.5)
    else:
        s += pa(f"M {cx-12},{my} Q {cx},{my+10} {cx+12},{my}",
                "none", P["mouth"], 3.5)

    # ── 眼鏡 (タクボ市長の最大特徴！) ──────────────────
    gx_l, gx_r = cx - 22, cx + 22
    gy = hy - 8
    gr = 17   # レンズ半径
    gcol = P["glasses"]
    gsw = 3.5
    # 左レンズ
    s += ci(gx_l, gy, gr, "none", gcol, gsw)
    # 右レンズ
    s += ci(gx_r, gy, gr, "none", gcol, gsw)
    # ブリッジ
    s += li(gx_l+gr, gy, gx_r-gr, gy, gcol, gsw)
    # テンプル (左)
    s += li(gx_l-gr, gy, gx_l-gr-18, gy-5, gcol, gsw)
    # テンプル (右)
    s += li(gx_r+gr, gy, gx_r+gr+18, gy-5, gcol, gsw)

    return s


def _takubo_body(cx, body_top, pose="normal"):
    """胴体・腕・スカート・脚を描く"""
    s = ""
    bt = body_top  # 胴体上端

    # ── 首 ──────────────────────────────────────────────
    s += rc(cx-10, bt-12, 20, 18, P["skin"], rx=6)

    # ── 胴体 (オレンジジャケット) ───────────────────────
    body_h = 75
    s += pa(
        f"M {cx-42},{bt} Q {cx-46},{bt+body_h} {cx-38},{bt+body_h+8} "
        f"L {cx+38},{bt+body_h+8} Q {cx+46},{bt+body_h} {cx+42},{bt} "
        f"Q {cx+20},{bt-6} {cx},{bt-4} Q {cx-20},{bt-6} Z",
        P["jacket"]
    )
    # 内側のハイライト
    s += pa(
        f"M {cx-30},{bt+4} Q {cx-26},{bt+body_h-10} {cx-16},{bt+body_h}",
        "none", P["jacket_s"] if False else "#FFB060", 3, extra='opacity="0.4"'
    )

    # ── 白い襟/インナー ─────────────────────────────────
    s += pa(
        f"M {cx-10},{bt} L {cx-15},{bt+body_h-5} L {cx},{bt+body_h+2} "
        f"L {cx+15},{bt+body_h-5} L {cx+10},{bt} Z",
        P["collar"], OL, 2
    )
    # ボタン (3つ)
    for i in range(3):
        by = bt + 18 + i * 20
        s += ci(cx, by, 4, P["jacket_s"], OL, 2)

    # ── 腕の分岐 ─────────────────────────────────────
    if pose == "victory":
        # 右腕を突き上げる
        # 左腕 (普通)
        s += pa(
            f"M {cx-42},{bt+8} Q {cx-58},{bt+45} {cx-52},{bt+68} "
            f"Q {cx-40},{bt+75} {cx-34},{bt+62} Q {cx-40},{bt+42} {cx-30},{bt+10} Z",
            P["jacket"]
        )
        s += el(cx-52, bt+72, 13, 11, P["skin"])
        # 右腕 (上へ!)
        s += pa(
            f"M {cx+42},{bt+8} Q {cx+58},{bt-10} {cx+62},{bt-50} "
            f"Q {cx+50},{bt-60} {cx+38},{bt-48} Q {cx+44},{bt-14} {cx+30},{bt+10} Z",
            P["jacket"]
        )
        s += el(cx+60, bt-54, 13, 12, P["skin"])
        # こぶし
        s += pa(f"M {cx+50},{bt-68} Q {cx+52},{bt-80} {cx+68},{bt-78} "
                f"Q {cx+72},{bt-68} {cx+70},{bt-60} Q {cx+58},{bt-58} Z",
                P["skin"])
    elif pose == "angry":
        # 両腕を広げる
        s += pa(
            f"M {cx-42},{bt+8} Q {cx-68},{bt+12} {cx-76},{bt+32} "
            f"Q {cx-64},{bt+42} {cx-56},{bt+30} Q {cx-50},{bt+15} {cx-30},{bt+10} Z",
            P["jacket"]
        )
        s += el(cx-80, bt+36, 13, 11, P["skin"])
        s += pa(
            f"M {cx+42},{bt+8} Q {cx+68},{bt+12} {cx+76},{bt+32} "
            f"Q {cx+64},{bt+42} {cx+56},{bt+30} Q {cx+50},{bt+15} {cx+30},{bt+10} Z",
            P["jacket"]
        )
        s += el(cx+80, bt+36, 13, 11, P["skin"])
    elif pose == "battle":
        # 右手を前に
        s += pa(
            f"M {cx-42},{bt+8} Q {cx-58},{bt+45} {cx-52},{bt+68} "
            f"Q {cx-40},{bt+75} {cx-34},{bt+62} Q {cx-40},{bt+42} {cx-30},{bt+10} Z",
            P["jacket"]
        )
        s += el(cx-52, bt+72, 13, 11, P["skin"])
        s += pa(
            f"M {cx+42},{bt+8} Q {cx+62},{bt+22} {cx+70},{bt+48} "
            f"Q {cx+58},{bt+58} {cx+50},{bt+46} Q {cx+44},{bt+26} {cx+30},{bt+10} Z",
            P["jacket"]
        )
        s += el(cx+74, bt+52, 13, 11, P["skin"])
    else:
        # 通常 両腕下げ
        s += pa(
            f"M {cx-42},{bt+8} Q {cx-58},{bt+45} {cx-52},{bt+68} "
            f"Q {cx-40},{bt+75} {cx-34},{bt+62} Q {cx-40},{bt+42} {cx-30},{bt+10} Z",
            P["jacket"]
        )
        s += el(cx-52, bt+72, 13, 11, P["skin"])
        s += pa(
            f"M {cx+42},{bt+8} Q {cx+58},{bt+45} {cx+52},{bt+68} "
            f"Q {cx+40},{bt+75} {cx+34},{bt+62} Q {cx+40},{bt+42} {cx+30},{bt+10} Z",
            P["jacket"]
        )
        s += el(cx+52, bt+72, 13, 11, P["skin"])

    # ── スカート ─────────────────────────────────────────
    sk_top = bt + body_h + 8
    sk_h = 50
    s += pa(
        f"M {cx-40},{sk_top} Q {cx-46},{sk_top+sk_h} {cx-40},{sk_top+sk_h+6} "
        f"L {cx+40},{sk_top+sk_h+6} Q {cx+46},{sk_top+sk_h} {cx+40},{sk_top} Z",
        P["skirt"]
    )
    # スカートのシャドウ
    s += pa(
        f"M {cx-40},{sk_top} Q {cx-44},{sk_top+30} {cx-38},{sk_top+sk_h+4}",
        "none", P["skirt_s"], 4, extra='opacity="0.5"'
    )

    # ── 脚 ──────────────────────────────────────────────
    leg_top = sk_top + sk_h + 6
    leg_h = 38
    s += rc(cx-28, leg_top, 20, leg_h, P["stocking"], rx=6)
    s += rc(cx+8,  leg_top, 20, leg_h, P["stocking"], rx=6)

    # ── 靴 ──────────────────────────────────────────────
    foot_y = leg_top + leg_h
    s += pa(
        f"M {cx-32},{foot_y} Q {cx-28},{foot_y+16} {cx-8},{foot_y+16} "
        f"Q {cx-2},{foot_y+10} {cx-6},{foot_y} Z",
        P["shoe"]
    )
    s += pa(
        f"M {cx+4},{foot_y} Q {cx+8},{foot_y+10} {cx+14},{foot_y+16} "
        f"Q {cx+34},{foot_y+16} {cx+38},{foot_y+6} Q {cx+34},{foot_y} Z",
        P["shoe"]
    )
    # 靴のつや
    s += pa(f"M {cx-26},{foot_y+2} Q {cx-22},{foot_y+6} {cx-18},{foot_y+4}",
            "none", "#888", 1.5)
    s += pa(f"M {cx+10},{foot_y+2} Q {cx+14},{foot_y+6} {cx+18},{foot_y+4}",
            "none", "#888", 1.5)

    return s


def takubo(cx=185, head_top=18, emotion="normal", body_pose="normal"):
    """タクボ市長の完全ちびキャラ"""
    hy = head_top + 72   # 頭の中心Y
    body_top = hy + 70   # 胴体上端

    s = _takubo_head(cx, hy, emotion)
    s += _takubo_body(cx, body_top, body_pose)
    return s


# ══════════════════════════════════════════════════════════
# 市議会キャラ (中年男性・スーツ)
# ══════════════════════════════════════════════════════════

def council(cx=185, head_top=18, emotion="normal"):
    hy = head_top + 72
    s = ""

    # ── 黒髪 (短く整えた) ──────────────────────────────
    s += pa(
        f"M {cx-62},{hy+15} Q {cx-72},{hy-25} {cx-46},{hy-74} "
        f"Q {cx-22},{hy-90} {cx},{hy-88} "
        f"Q {cx+22},{hy-90} {cx+46},{hy-74} "
        f"Q {cx+72},{hy-25} {cx+62},{hy+15} Z",
        P["c_hair"], OL, SW
    )
    # つむじ線
    s += pa(f"M {cx-8},{hy-84} Q {cx},{hy-88} {cx+8},{hy-84}",
            "none", "#444", 2)
    # サイドの影
    s += pa(f"M {cx-60},{hy+10} Q {cx-65},{hy+25} {cx-58},{hy+36}",
            "none", "#111", 3)
    s += pa(f"M {cx+60},{hy+10} Q {cx+65},{hy+25} {cx+58},{hy+36}",
            "none", "#111", 3)

    # ── 顔 ──────────────────────────────────────────────
    s += el(cx, hy, 60, 68, P["skin"])

    # ほっぺ
    s += el(cx-38, hy+18, 14, 9, P["cheek"], stroke="none", sw=0, extra='opacity="0.5"')
    s += el(cx+38, hy+18, 14, 9, P["cheek"], stroke="none", sw=0, extra='opacity="0.5"')

    # ── 眉 ──────────────────────────────────────────────
    if emotion == "smug":
        s += pa(f"M {cx-30},{hy-24} Q {cx-20},{hy-30} {cx-8},{hy-25}",
                "none", P["c_hair"], 4)
        s += pa(f"M {cx+30},{hy-32} Q {cx+20},{hy-24} {cx+8},{hy-28}",
                "none", P["c_hair"], 4.5)
    elif emotion == "angry":
        s += pa(f"M {cx-30},{hy-30} L {cx-8},{hy-22}", "none", P["c_hair"], 4.5)
        s += pa(f"M {cx+30},{hy-30} L {cx+8},{hy-22}", "none", P["c_hair"], 4.5)
    else:
        s += pa(f"M {cx-30},{hy-26} Q {cx-20},{hy-32} {cx-8},{hy-27}",
                "none", P["c_hair"], 4)
        s += pa(f"M {cx+30},{hy-26} Q {cx+20},{hy-32} {cx+8},{hy-27}",
                "none", P["c_hair"], 4)

    # ── 目 ──────────────────────────────────────────────
    ex_l, ex_r = cx - 22, cx + 22
    ey = hy - 8

    if emotion == "smug":
        s += el(ex_l, ey+2, 13, 9, "#DDEEDD")
        s += el(ex_r, ey+2, 13, 9, "#DDEEDD")
        s += ci(ex_l-2, ey+3, 7, P["eye"])
        s += ci(ex_r+2, ey+3, 7, P["eye"])
        # 上まぶた (半目)
        s += pa(f"M {ex_l-14},{ey+3} Q {ex_l},{ey-8} {ex_l+14},{ey+3}",
                P["skin"], stroke="none")
        s += pa(f"M {ex_r-14},{ey+3} Q {ex_r},{ey-8} {ex_r+14},{ey+3}",
                P["skin"], stroke="none")
        s += pa(f"M {ex_l-14},{ey+3} Q {ex_l},{ey-8} {ex_l+14},{ey+3}",
                "none", OL, 3)
        s += pa(f"M {ex_r-14},{ey+3} Q {ex_r},{ey-8} {ex_r+14},{ey+3}",
                "none", OL, 3)
        s += ci(ex_l-3, ey-1, 2.5, P["pupil_hi"], stroke="none")
        s += ci(ex_r+1, ey-1, 2.5, P["pupil_hi"], stroke="none")
    elif emotion == "angry":
        s += pa(f"M {ex_l-13},{ey-4} Q {ex_l},{ey+8} {ex_l+12},{ey-2} "
                f"Q {ex_l},{ey+16} {ex_l-13},{ey+6} Z", P["eye"])
        s += pa(f"M {ex_r-12},{ey-2} Q {ex_r},{ey+8} {ex_r+13},{ey-4} "
                f"Q {ex_r+13},{ey+6} {ex_r},{ey+16} Z", P["eye"])
        s += ci(ex_l-2, ey+2, 2.5, P["pupil_hi"], stroke="none")
        s += ci(ex_r+2, ey+2, 2.5, P["pupil_hi"], stroke="none")
    else:
        s += el(ex_l, ey, 13, 15, "#E8EEFF")
        s += el(ex_r, ey, 13, 15, "#E8EEFF")
        s += ci(ex_l, ey+1, 9, P["eye"])
        s += ci(ex_r, ey+1, 9, P["eye"])
        s += ci(ex_l-3, ey-3, 3, P["pupil_hi"], stroke="none")
        s += ci(ex_r-3, ey-3, 3, P["pupil_hi"], stroke="none")
        s += el(ex_l, ey, 13, 15, "none", OL, SW)
        s += el(ex_r, ey, 13, 15, "none", OL, SW)

    # 鼻
    s += ci(cx, hy+8, 3.5, P["skin_s"], stroke="none")

    # ── 口 ──────────────────────────────────────────────
    my = hy + 32
    if emotion == "smug":
        s += pa(f"M {cx-4},{my+2} Q {cx+4},{my+14} {cx+18},{my}",
                "none", P["mouth"], 3.5)
    elif emotion == "angry":
        s += pa(f"M {cx-16},{my+6} Q {cx},{my} {cx+16},{my+6}",
                P["teeth"])
        s += pa(f"M {cx-16},{my+6} Q {cx},{my} {cx+16},{my+6}",
                "none", P["mouth"], 3.5)
    else:
        s += pa(f"M {cx-12},{my} Q {cx},{my+9} {cx+12},{my}",
                "none", P["mouth"], 3.5)

    # ── 胴体 (スーツ) ───────────────────────────────────
    body_top = hy + 70
    bt = body_top
    body_h = 75

    # 首
    s += rc(cx-10, bt-12, 20, 18, P["skin"], rx=6)

    # スーツ
    s += pa(
        f"M {cx-42},{bt} Q {cx-46},{bt+body_h} {cx-38},{bt+body_h+8} "
        f"L {cx+38},{bt+body_h+8} Q {cx+46},{bt+body_h} {cx+42},{bt} "
        f"Q {cx+20},{bt-6} {cx},{bt-4} Q {cx-20},{bt-6} Z",
        P["c_suit"]
    )
    # シャツ
    s += pa(
        f"M {cx-10},{bt} L {cx-14},{bt+body_h-4} L {cx},{bt+body_h+2} "
        f"L {cx+14},{bt+body_h-4} L {cx+10},{bt} Z",
        P["c_shirt"], OL, 2
    )
    # ネクタイ
    s += pa(
        f"M {cx-5},{bt+4} L {cx+5},{bt+4} L {cx+8},{bt+30} "
        f"L {cx+4},{bt+body_h-2} L {cx},{bt+body_h+2} "
        f"L {cx-4},{bt+body_h-2} L {cx-8},{bt+30} Z",
        P["c_tie"], OL, 2
    )
    # ネクタイノット
    s += pa(f"M {cx-5},{bt+4} L {cx+5},{bt+4} L {cx},{bt+14} Z",
            P["c_tie"], OL, 1.5)

    # 腕
    if emotion == "angry":
        s += pa(
            f"M {cx-42},{bt+8} Q {cx-68},{bt+14} {cx-74},{bt+34} "
            f"Q {cx-62},{bt+44} {cx-54},{bt+32} Q {cx-50},{bt+16} {cx-30},{bt+10} Z",
            P["c_suit"]
        )
        s += el(cx-78, bt+38, 12, 10, P["skin"])
        s += pa(
            f"M {cx+42},{bt+8} Q {cx+68},{bt+14} {cx+74},{bt+34} "
            f"Q {cx+62},{bt+44} {cx+54},{bt+32} Q {cx+50},{bt+16} {cx+30},{bt+10} Z",
            P["c_suit"]
        )
        s += el(cx+78, bt+38, 12, 10, P["skin"])
    else:
        s += pa(
            f"M {cx-42},{bt+8} Q {cx-58},{bt+46} {cx-52},{bt+70} "
            f"Q {cx-40},{bt+76} {cx-34},{bt+62} Q {cx-40},{bt+44} {cx-30},{bt+10} Z",
            P["c_suit"]
        )
        s += el(cx-52, bt+72, 12, 10, P["skin"])
        s += pa(
            f"M {cx+42},{bt+8} Q {cx+58},{bt+46} {cx+52},{bt+70} "
            f"Q {cx+40},{bt+76} {cx+34},{bt+62} Q {cx+40},{bt+44} {cx+30},{bt+10} Z",
            P["c_suit"]
        )
        s += el(cx+52, bt+72, 12, 10, P["skin"])

    # ズボン
    sk_top = bt + body_h + 8
    sk_h = 50
    s += pa(
        f"M {cx-40},{sk_top} Q {cx-46},{sk_top+sk_h} {cx-40},{sk_top+sk_h+6} "
        f"L {cx+40},{sk_top+sk_h+6} Q {cx+46},{sk_top+sk_h} {cx+40},{sk_top} Z",
        P["c_suit_s"]
    )
    # センタープレス
    s += li(cx, sk_top, cx, sk_top+sk_h+4, "#8890B0", 1.5)

    # 脚・靴
    leg_top = sk_top + sk_h + 6
    leg_h = 38
    s += rc(cx-28, leg_top, 20, leg_h, P["c_suit_s"], rx=6)
    s += rc(cx+8,  leg_top, 20, leg_h, P["c_suit_s"], rx=6)
    foot_y = leg_top + leg_h
    s += pa(
        f"M {cx-32},{foot_y} Q {cx-28},{foot_y+16} {cx-8},{foot_y+16} "
        f"Q {cx-2},{foot_y+10} {cx-6},{foot_y} Z",
        P["shoe"]
    )
    s += pa(
        f"M {cx+4},{foot_y} Q {cx+8},{foot_y+10} {cx+14},{foot_y+16} "
        f"Q {cx+34},{foot_y+16} {cx+38},{foot_y+6} Q {cx+34},{foot_y} Z",
        P["shoe"]
    )

    return s


# ══════════════════════════════════════════════════════════
# 10枚のスタンプ定義
# ══════════════════════════════════════════════════════════

def make_01_normal():
    """01: タクボ 通常 — にっこり手を振る"""
    s = svg_open()
    # ハート飾り
    s += heart(50, 60, 14, P["heart"], stroke=P["mouth"], sw=2)
    s += heart(310, 80, 10, P["heart"], stroke=P["mouth"], sw=2)
    # キャラ
    s += takubo(emotion="normal", body_pose="normal")
    # 吹き出し
    s += speech_bubble(220, 36, 110, 44, 242, 80)
    s += tx(275, 65, "よろしく！", size=17)
    s += svg_close()
    return s

def make_02_victory():
    """02: タクボ ガッツ — 右手突き上げ大笑顔"""
    s = svg_open()
    # エフェクト光線
    for i in range(8):
        a = math.radians(i * 45)
        x2 = 185 + 200 * math.cos(a)
        y2 = 155 + 200 * math.sin(a)
        s += li(185, 155, x2, y2, P["yellow"], 8, "round")
        s += li(185, 155, x2, y2, "#FFF8A0", 4, "round")
    # 星
    for (sx, sy, sr) in [(60, 40, 12), (308, 50, 10), (50, 240, 9), (320, 200, 11)]:
        s += star_shape(sx, sy, sr, sr*0.45, 5, P["star"], OL, 1.5)
    s += takubo(emotion="victory", body_pose="victory")
    # ガッツポーズ吹き出し
    s += speech_bubble(200, 30, 130, 46, 230, 78)
    s += tx(265, 60, "やったぞ！", size=17)
    s += svg_close()
    return s

def make_03_angry():
    """03: タクボ 怒り — 両腕広げ叫ぶ"""
    s = svg_open()
    # 怒りオーラ
    for i in range(6):
        a = math.radians(i * 60 + 10)
        x2 = 185 + 180 * math.cos(a)
        y2 = 145 + 180 * math.sin(a)
        s += li(185, 145, x2, y2, "#FF4020", 6)
    s += takubo(emotion="angry", body_pose="angry")
    # 怒りマーク
    s += pa("M 298,55 L 308,40 L 318,55 L 308,52 Z", P["red"])
    s += pa("M 308,52 L 308,64", "none", P["red"], 5)
    # 吹き出し
    s += speech_bubble(30, 50, 112, 46, 100, 95)
    s += tx(86, 80, "もう限界！", size=16)
    s += svg_close()
    return s

def make_04_crying():
    """04: タクボ 泣き — 大泣き"""
    s = svg_open()
    # 雨のような涙の粒
    for (tx2, ty2, tr) in [(80, 260, 6), (90, 280, 4), (270, 265, 5), (285, 285, 4)]:
        s += el(tx2, ty2, tr, tr*1.5, P["tear"], stroke=P["blue"], sw=1.5)
    s += takubo(emotion="crying", body_pose="normal")
    s += speech_bubble(210, 32, 126, 46, 240, 78)
    s += tx(273, 62, "うわーん！", size=16)
    s += svg_close()
    return s

def make_05_battle():
    """05: タクボ バトル — 構えポーズ"""
    s = svg_open()
    # 後光エフェクト
    for i in range(10):
        a = math.radians(i * 36)
        x2 = 185 + 180 * math.cos(a)
        y2 = 145 + 180 * math.sin(a)
        col = P["yellow"] if i % 2 == 0 else P["orange"]
        s += li(185, 145, x2, y2, col, 5)
    s += takubo(emotion="battle", body_pose="battle")
    s += speech_bubble(196, 28, 136, 46, 230, 76)
    s += tx(264, 58, "受けて立つ！", size=15)
    s += svg_close()
    return s

def make_06_council_smug():
    """06: 市議会 ニヤリ"""
    s = svg_open()
    # ダーク背景ライン
    for i in range(5):
        s += li(0, 60 + i*40, 370, 60 + i*40, "#E8EFF8", 1)
    s += council(emotion="smug")
    # ニヤリ吹き出し
    s += speech_bubble(196, 28, 144, 50, 228, 78)
    s += tx(268, 52, "ふっ…", size=17)
    s += tx(268, 72, "甘いな", size=17)
    s += svg_close()
    return s

def make_07_council_angry():
    """07: 市議会 不信任動議"""
    s = svg_open()
    # 赤い雰囲気
    for i in range(4):
        a = math.radians(i * 45 + 22)
        x2 = 185 + 200 * math.cos(a)
        y2 = 145 + 200 * math.sin(a)
        s += li(185, 145, x2, y2, "#FF2020", 5, "round")
    s += council(emotion="angry")
    # 不信任状 (斜め)
    s += rc(40, 198, 110, 80, "#FEFEE8", OL, 2.5, rx=4,
            extra='transform="rotate(-8 95 238)"')
    s += f'<text x="95" y="228" font-size="15" font-weight="bold" font-family="sans-serif" fill="{P["red"]}" text-anchor="middle" transform="rotate(-8 95 238)">不信任</text>\n'
    s += f'<text x="95" y="250" font-size="15" font-weight="bold" font-family="sans-serif" fill="{OL}" text-anchor="middle" transform="rotate(-8 95 238)">動議！！</text>\n'
    s += svg_close()
    return s

def make_08_vs():
    """08: タクボ VS 市議会 対決"""
    s = svg_open()
    # 放射バースト
    for i in range(16):
        a = math.radians(i * 22.5)
        x2 = 185 + 280 * math.cos(a)
        y2 = 155 + 280 * math.sin(a)
        col = P["yellow"] if i % 2 == 0 else "#FFF4B0"
        s += li(185, 155, x2, y2, col, 14)
    # 対角分割
    s += pa("M 0,0 L 185,155 L 370,0 Z", "#FFF8E0", stroke="none")
    s += pa("M 0,320 L 185,155 L 370,320 Z", "#E8F0FF", stroke="none")

    # タクボ (左, 小さめ)
    s += f'<g transform="translate(-72,12) scale(0.82,0.82)">\n'
    s += takubo(cx=185, emotion="battle", body_pose="battle")
    s += "</g>\n"
    # 市議会 (右, ミラー)
    s += f'<g transform="translate(443,12) scale(-0.82,0.82)">\n'
    s += council(cx=185, emotion="angry")
    s += "</g>\n"

    # VS バッジ
    s += ci(185, 155, 34, P["red"])
    s += ci(185, 155, 30, "#FF4040")
    s += tx(185, 163, "VS", size=28, fill="white")

    s += svg_close()
    return s

def make_main_cover():
    s = svg_open(240, 240)
    # 背景グラデーション風
    s += rc(0, 0, 240, 240, "#FFF8F0", stroke="none", sw=0)
    s += el(120, 120, 118, 118, "#FFF0E0", stroke="#F4C080", sw=3)
    # キャラ (小さく)
    s += f'<g transform="translate(-68,-14) scale(0.78,0.78)">\n'
    s += takubo(cx=185, emotion="normal", body_pose="normal")
    s += "</g>\n"
    # ロゴ
    s += rc(20, 192, 200, 34, P["jacket"], stroke=P["jacket_s"], sw=2, rx=10)
    s += tx(120, 215, "タクボ市長スタンプ", size=15, fill="white")
    s += svg_close()
    return s

def make_tab_icon():
    s = svg_open(96, 74)
    s += rc(0, 0, 96, 74, "#FFF8F0", stroke="none")
    s += el(48, 37, 47, 36, "#FFE8C0", stroke=P["jacket"], sw=2)
    # 頭だけ表示 (超小)
    s += f'<g transform="translate(-107,-8) scale(0.38,0.38)">\n'
    hy = 18 + 72
    s += _takubo_head(185, hy, "normal")
    s += "</g>\n"
    s += svg_close()
    return s


# ── スタンプ一覧 ────────────────────────────────────────
STICKERS = {
    "01_takubo_normal":     (make_01_normal,    (370, 320)),
    "02_takubo_victory":    (make_02_victory,   (370, 320)),
    "03_takubo_angry":      (make_03_angry,     (370, 320)),
    "04_takubo_sad":        (make_04_crying,    (370, 320)),
    "05_takubo_battle":     (make_05_battle,    (370, 320)),
    "06_council_smug":      (make_06_council_smug, (370, 320)),
    "07_council_angry":     (make_07_council_angry, (370, 320)),
    "08_takubo_vs_council": (make_08_vs,        (370, 320)),
    "main_cover":           (make_main_cover,   (240, 240)),
    "tab_icon":             (make_tab_icon,     (96, 74)),
}


def svg_to_png(svg_str, w, h):
    return cairosvg.svg2png(bytestring=svg_str.encode("utf-8"),
                            output_width=w, output_height=h)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", nargs="*", default=None)
    parser.add_argument("--svg-only", action="store_true")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    global OUTPUT_DIR
    if args.output_dir:
        OUTPUT_DIR = Path(args.output_dir)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SVG_DIR.mkdir(parents=True, exist_ok=True)

    targets = args.ids or list(STICKERS.keys())
    print(f"=== SVGスタンプ生成 ({len(targets)} 枚) ===\n")

    for sid in targets:
        if sid not in STICKERS:
            print(f"  [SKIP] {sid}")
            continue
        fn, (w, h) = STICKERS[sid]
        print(f"  {sid} ({w}×{h}) ...", end="", flush=True)
        svg_str = fn()
        (SVG_DIR / f"{sid}.svg").write_text(svg_str, encoding="utf-8")
        if not args.svg_only:
            png = svg_to_png(svg_str, w, h)
            out = OUTPUT_DIR / f"{sid}.png"
            out.write_bytes(png)
            kb = len(png) / 1024
            warn = " ⚠500KB超" if kb > 500 else ""
            print(f" OK ({kb:.0f}KB){warn}")
        else:
            print(" SVG保存")

    print(f"\n完了 → {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
