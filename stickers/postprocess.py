"""
後処理ユーティリティ: クロマキーグリーン除去 + LINEスタンプ規定サイズへのリサイズ

参考: https://github.com/philschmid/gemini-samples/blob/main/examples/interactions-generate-stickers.ipynb
"""

import numpy as np
from PIL import Image


# LINE スタンプ規定サイズ
LINE_STICKER_SIZE = (370, 320)
LINE_MAIN_SIZE    = (240, 240)
LINE_TAB_SIZE     = (96, 74)

# クロマキーグリーン (#00FF00) のHSV範囲
_GREEN_HUE_LOW  = 40   # 色相下限 (0-179 in OpenCV scale, PIL uses 0-360)
_GREEN_HUE_HIGH = 80   # 色相上限
_GREEN_SAT_MIN  = 150  # 彩度下限 (0-255)
_GREEN_VAL_MIN  = 100  # 明度下限 (0-255)


def remove_chromakey_green(img: Image.Image, expand_mask: int = 2) -> Image.Image:
    """
    クロマキーグリーン (#00FF00) 背景をアルファ透過に変換する。

    expand_mask: アンチエイリアス対策のマスク膨張ピクセル数
    """
    rgba = img.convert("RGBA")
    data = np.array(rgba, dtype=np.float32)

    r, g, b = data[:, :, 0], data[:, :, 1], data[:, :, 2]

    # HSV変換 (PIL/numpy で計算、OpenCV不要)
    r_n, g_n, b_n = r / 255.0, g / 255.0, b / 255.0
    cmax = np.maximum(np.maximum(r_n, g_n), b_n)
    cmin = np.minimum(np.minimum(r_n, g_n), b_n)
    delta = cmax - cmin

    # 色相 (0-360)
    hue = np.zeros_like(cmax)
    mask_g = (cmax == g_n) & (delta > 0)
    mask_b = (cmax == b_n) & (delta > 0)
    mask_r = (cmax == r_n) & (delta > 0)
    hue[mask_r] = (60 * ((g_n - b_n) / delta % 6))[mask_r]
    hue[mask_g] = (60 * ((b_n - r_n) / delta + 2))[mask_g]
    hue[mask_b] = (60 * ((r_n - g_n) / delta + 4))[mask_b]
    hue = hue % 360

    # 彩度 (0-255 スケール)
    sat = np.where(cmax > 0, delta / cmax * 255, 0)
    # 明度 (0-255 スケール)
    val = cmax * 255

    # グリーン範囲マスク (HSVベース)
    hue_lo, hue_hi = 80, 160   # 360度スケール
    green_mask = (
        (hue >= hue_lo) & (hue <= hue_hi) &
        (sat >= _GREEN_SAT_MIN) &
        (val >= _GREEN_VAL_MIN)
    )

    # 追加: RGBベースで純粋なグリーン系も除去 (g >> r, b)
    rgb_green = (g > r * 1.3) & (g > b * 1.3) & (g > 100)
    green_mask = green_mask | rgb_green

    # マスク膨張 (アンチエイリアス対策)
    if expand_mask > 0:
        from scipy.ndimage import binary_dilation
        green_mask = binary_dilation(green_mask, iterations=expand_mask)

    # アルファチャンネルに適用
    alpha = np.where(green_mask, 0, 255).astype(np.uint8)
    result = np.dstack([data[:, :, :3].astype(np.uint8), alpha])

    return Image.fromarray(result, "RGBA")


def resize_for_line(
    img: Image.Image,
    target: tuple[int, int],
    pad_color: tuple[int, int, int, int] = (0, 0, 0, 0),
) -> Image.Image:
    """
    アスペクト比を維持して target サイズにリサイズし、透過パディングを加える。
    """
    img = img.convert("RGBA")
    w, h = img.size
    tw, th = target

    scale = min(tw / w, th / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = img.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGBA", target, pad_color)
    offset_x = (tw - new_w) // 2
    offset_y = (th - new_h) // 2
    canvas.paste(resized, (offset_x, offset_y), resized)
    return canvas


def process_sticker_image(
    img: Image.Image,
    sticker_id: str,
) -> Image.Image:
    """
    クロマキー除去 + サイズ変換を一括実行。
    sticker_id が 'main_cover' → 240x240, 'tab_icon' → 96x74, それ以外 → 370x320。
    """
    img = remove_chromakey_green(img)

    if sticker_id == "main_cover":
        return resize_for_line(img, LINE_MAIN_SIZE)
    elif sticker_id == "tab_icon":
        return resize_for_line(img, LINE_TAB_SIZE)
    else:
        return resize_for_line(img, LINE_STICKER_SIZE)
