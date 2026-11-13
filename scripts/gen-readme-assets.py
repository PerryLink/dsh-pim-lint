#!/usr/bin/env python3
"""Generate README visuals for dsh-pim-lint (docs/assets/).

Outputs (idempotent overwrite):
  dsh-pim-lint-hero-{zh,en}-{light,dark}.webp   1440x576 raster hero (Pillow)
  dsh-pim-lint-flow-v5-{light,dark}.svg         1100x660 hand-written SVG

Design notes
------------
* Hero: the left column is prose (kicker / title / two value lines / one
  subtitle / one meta line / one footer). The right column is this
  repository's own semantic figure: a 12-row `catalog.csv` sheet with three
  real fixture issues attached as `issues[]` cards (SKU-1004 / gtin /
  E_PIM_GTIN_INVALID, SKU-1005 / price / E_PIM_PRICE_PRECISION, SKU-1008 /
  title / E_PIM_TITLE_REQUIRED), and underneath it the actual GTIN-14
  variable-measure sample 94006381333934 laid out as a check-digit ruler
  (3/1 weights, check digit 4, indicator 9, variable_measure true). All
  numbers and codes come from samples/quickstart/expected/result.json.
* Flow: a two-channel structure, NOT a row of nodes. Channel A is whole-table
  `pim_validate`: catalog.csv -> CSV guard (three throw-only codes) -> 12 rows
  -> a 4-field x 7-rule inspection matrix -> `issues[]` keyed by
  SKU/field/code. Channel B is the single-code bench: a 14-digit GTIN through
  `pim_gtin_check`/`pim_gtin_structure` (format, indicator, variable_measure)
  and an 18-digit SSCC through `pim_sscc_check` (format vs mod-10 reason).
  The bottom band gives the three real return shapes. Text is tokens, field
  names and short labels only, so all five README languages share one pair.
  The matrix counts are the fixture's: 8 issues, 6 codes, sku x1 / title x1 /
  gtin x4 / price x2.
* The older `dsh-pim-lint-flow{,-light,-dark}.svg` files plus the PNG
  captures in docs/assets/ are historical evidence kept for external links;
  this script now writes only the hero set and the flow-v5 pair above.

Run once:  python scripts/gen-readme-assets.py
Requires:  Python 3.10+ with Pillow; Windows fonts msyh.ttc / msyhbd.ttc /
           consola.ttf / consolab.ttf / segoeui.ttf / segoeuib.ttf.
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

FONT_CJK = r"C:\Windows\Fonts\msyh.ttc"
FONT_CJK_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"
FONT_MONO_BOLD = r"C:\Windows\Fonts\consolab.ttf"
FONT_EN = r"C:\Windows\Fonts\segoeui.ttf"
FONT_EN_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"

for _path in (FONT_CJK, FONT_CJK_BOLD, FONT_MONO, FONT_MONO_BOLD,
              FONT_EN, FONT_EN_BOLD):
    if not os.path.exists(_path):
        raise SystemExit(f"FATAL: font missing: {_path}")

WARNINGS: list[str] = []

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8", card="#ffffff",
        card_edge="#e4e1ee", sheet="#f8f5fc", sheet_edge="#e7e2f2",
        zone="#f7f4fc", zone_edge="#e5e0f1", text="#141419",
        sub="#4d5261", faint="#8f94a4", accent="#4B67B4",
        pill="#ece7f9", grid="#e7e4f0", good="#16a34a",
        bad="#b42318", bad_soft="#fdf0ee", warn="#b45309",
        warn_soft="#fdf6e8", dot="#d9d3ea", shadow=(32, 26, 64),
        on_accent="#ffffff",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016", card="#1b2231",
        card_edge="#2e374b", sheet="#171e2d", sheet_edge="#2b3448",
        zone="#161d2c", zone_edge="#2a3348", text="#f0f3f9",
        sub="#a8b1c4", faint="#737b8d", accent="#8496f5",
        pill="#242d42", grid="#1e2636", good="#3fb950",
        bad="#f0883e", bad_soft="#33241c", warn="#d9a03c",
        warn_soft="#332a1a", dot="#26314a", shadow=(0, 0, 0),
        on_accent="#0c1016",
    ),
}


# --------------------------------------------------------------- primitives
def font(size, kind="cjk"):
    return ImageFont.truetype(
        {"cjk": FONT_CJK, "cjk_bold": FONT_CJK_BOLD, "mono": FONT_MONO,
         "mono_bold": FONT_MONO_BOLD, "en": FONT_EN,
         "en_bold": FONT_EN_BOLD}[kind], max(8, int(size)))


def hx(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(p + (q - p) * t) for p, q in zip(hx(a), hx(b)))


def gradient(w, h, c1, c2):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = 0.22 * (y / h) + 0.78 * (y / h) ** 1.5
        d.line([(0, y), (w, y)], fill=mix(c1, c2, t))
    return img


def glow(img, cx, cy, r, color, alpha=30):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(14, 0, -1):
        rr = r * i / 14
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=color + (int(alpha * (1 - i / 15)),))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def dot_texture(img, color, alpha=14, spacing=30, r=1.2):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(0, img.height, spacing):
        for x in range(0, img.width, spacing):
            d.ellipse([x - r, y - r, x + r, y + r], fill=color + (alpha,))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def card(img, box, skin, radius=22, shadow=26, fill=None, edge=None, width=1.5):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(shadow, 0, -3):
        sd.rounded_rectangle([x0 - i // 6, y0 + i // 2, x1 + i // 6, y1 + i],
                             radius=radius + i // 6,
                             fill=skin["shadow"] + (int(9 * (1 - i / shadow)),))
    base = Image.alpha_composite(
        img.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(fill or skin["card"]),
                        outline=hx(edge or skin["card_edge"]),
                        width=max(1, int(round(width))))
    return base.convert("RGB")


def pill(img, xy, text, skin, size=20, kind="cjk_bold", fg=None, bg=None,
         anchor="la", padx=18, pady=10, outline=None):
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    tw = d.textlength(text, font=f)
    h = size + pady * 2
    x, y = xy
    if anchor == "ra":
        x -= tw + padx * 2
    d.rounded_rectangle([x, y, x + tw + padx * 2, y + h], radius=h // 2,
                        fill=hx(bg or skin["pill"]),
                        outline=hx(outline) if outline else None, width=2)
    d.text((x + padx, y + pady - 1), text, font=f, fill=hx(fg or skin["accent"]))
    return img


def fit(d, text, kind, max_w, size, min_size=10):
    size = int(size)
    while size > min_size:
        if d.textlength(text, font=font(size, kind)) <= max_w:
            return size
        size -= 1
    return max(min_size, size)


def write(img, xy, text, skin, size, kind="cjk", color="text",
          max_w=None, min_size=10, tag="", anchor=None):
    d = ImageDraw.Draw(img)
    if max_w is not None:
        size = fit(d, text, kind, max_w, size, min_size)
        if d.textlength(text, font=font(size, kind)) > max_w:
            WARNINGS.append(f"{tag}: {text!r} exceeds {max_w}px at {size}px")
    d.text(xy, text, font=font(size, kind), fill=hx(skin[color]),
           anchor=anchor)
    return size


# --------------------------------------------------------------- hero model
HERO = {
    "zh": dict(
        kicker="DeepSeek Harness · PIM 目录 lint 插件",
        title="dsh-pim-lint",
        value=["上线前，把重复 SKU、坏 GTIN 校验位",
               "和价格精度问题，一次列清。"],
        sub="四个 R0 工具 · 只读、本地、不联网、不调模型",
        meta="GTIN-8/12/13/14 · SSCC 18 位 · 12 个错误码",
        foot="Apache-2.0 · 不调用模型 · 合成样例 12 行 · 原文件不改",
        sheet_note="8 条问题 · 6 个错误码 · 每行只报 SKU / 字段 / 错误码",
        rows=["木柄硅胶铲", "陶瓷马克杯 350ml", "玻璃收纳罐 1L", "（空）"],
        issue_head="issues[] · 8",
        issue_codes=[("gtin", "E_PIM_GTIN_INVALID", "SKU-1004", "bad"),
                     ("price", "E_PIM_PRICE_PRECISION", "SKU-1005", "warn"),
                     ("title", "E_PIM_TITLE_REQUIRED", "SKU-1008", "bad")],
        bar_note="3·1 加权求和 → mod-10 → 校验位 4",
        bar_meta="indicator 9 · variable_measure",
        bar_note2="首位决定 indicator：0 基础 / 1–8 包装 / 9 变度量；"
                  "SSCC 18 位先剔空白",
        bar_note3="GTIN-8/12/13/14 只认纯数字；位数或字符不符一律不合法",
    ),
    "en": dict(
        kicker="DeepSeek Harness · PIM catalog lint plugin",
        title="dsh-pim-lint",
        value=["Duplicate SKUs, bad GTIN check digits,",
               "malformed prices — caught before launch."],
        sub="Four R0 tools · local, read-only, no network",
        meta="GTIN-8/12/13/14 · SSCC 18-digit · 12 error codes",
        foot="Apache-2.0 · no model call · 12-row synthetic sample · "
             "input untouched",
        sheet_note="8 issues · 6 error codes · each row is SKU / field / code",
        rows=["Silicone spatula", "Ceramic mug 350ml", "Glass jar 1L",
              "(empty)"],
        issue_head="issues[] · 8",
        issue_codes=[("gtin", "E_PIM_GTIN_INVALID", "SKU-1004", "bad"),
                     ("price", "E_PIM_PRICE_PRECISION", "SKU-1005", "warn"),
                     ("title", "E_PIM_TITLE_REQUIRED", "SKU-1008", "bad")],
        bar_note="3·1 weighted sum → mod-10 → check digit 4",
        bar_meta="indicator 9 · variable_measure",
        bar_note2="Leading digit is the indicator: 0 base / 1–8 packaging / "
                  "9 variable; SSCC is 18 digits after whitespace is stripped",
        bar_note3="GTIN-8/12/13/14 accept digits only; wrong length or "
                  "character is invalid",
    ),
}

ROWS = [
    ("SKU-1012", "6901234567915", "29.90", None),
    ("SKU-1004", "4006381333932", "45.00", "bad"),
    ("SKU-1005", "6901234567892", "39.999", "warn"),
    ("SKU-1008", "6901234567908", "25.00", "bad"),
]


def draw_sheet(img, s, hm, zh):
    x0, y0, x1, y1 = 700, 44, 1164, 304
    img = card(img, (x0, y0, x1, y1), s, radius=22)
    d = ImageDraw.Draw(img)
    write(img, (x0 + 24, y0 + 20), "catalog.csv", s, 19, "mono_bold",
          "text", 300, 14, "hero.sheet_title")
    d.text((x1 - 24, y0 + 25), "4 / 12 行" if zh else "4 / 12 rows",
           font=font(11, "cjk" if zh else "en"), fill=hx(s["faint"]),
           anchor="ra")
    cols = [("sku", x0 + 24), ("title", x0 + 102), ("gtin", x0 + 252),
            ("price", x1 - 24)]
    for label, x in cols:
        d.text((x, y0 + 55), label, font=font(11, "mono"),
               fill=hx(s["faint"]),
               anchor="ra" if label == "price" else "la")
    d.line([x0 + 24, y0 + 68, x1 - 24, y0 + 68], fill=hx(s["grid"]), width=1)
    for i, ((sku, gtin, price, tone), title) in enumerate(zip(ROWS, hm["rows"])):
        top = y0 + 75 + i * 37
        base = top + 26
        if tone:
            tint = s["bad_soft"] if tone == "bad" else s["warn_soft"]
            d.rounded_rectangle([x0 + 15, top, x1 - 15, top + 31], radius=9,
                                fill=hx(tint))
            d.rounded_rectangle([x0 + 15, top + 5, x0 + 18, top + 26], radius=2,
                                fill=hx(s["bad"] if tone == "bad" else s["warn"]))
        d.text((x0 + 24, base), sku, font=font(12.5, "mono"),
               fill=hx(s["text"]), anchor="ls")
        if i == 3:
            d.text((x0 + 102, base), title, font=font(11.5, "cjk" if zh else "en"),
                   fill=hx(s["bad"]), anchor="ls")
        else:
            d.text((x0 + 102, base), title,
                   font=font(12, "cjk" if zh else "en"),
                   fill=hx(s["text"]), anchor="ls")
        d.text((x0 + 252, base), gtin, font=font(12, "mono"),
               fill=hx(s["bad"] if i == 1 else s["text"]), anchor="ls")
        d.text((x1 - 24, base), price, font=font(12, "mono"),
               fill=hx(s["warn"] if i == 2 else s["text"]), anchor="rs")
    d.text((x0 + 24, y0 + 234), hm["sheet_note"],
           font=font(fit(d, hm["sheet_note"], "cjk" if zh else "en", 392, 11.5),
                    "cjk" if zh else "en"), fill=hx(s["sub"]))
    return img


def draw_issue_rail(img, s, hm, zh):
    x0, y0, x1, y1 = 1176, 44, 1380, 304
    img = card(img, (x0, y0, x1, y1), s, radius=22)
    d = ImageDraw.Draw(img)
    d.text((x0 + 22, y0 + 22), hm["issue_head"], font=font(13, "mono_bold"),
           fill=hx(s["accent"]))
    d.text((x1 - 22, y0 + 25), "3 / 8", font=font(10.5, "mono"),
           fill=hx(s["faint"]), anchor="ra")
    d.line([x0 + 16, y0 + 40, x1 - 16, y0 + 40], fill=hx(s["grid"]), width=1)
    for i, (field, code, sku, tone) in enumerate(hm["issue_codes"]):
        top = y0 + 50 + i * 66
        tint = s["bad_soft"] if tone == "bad" else s["warn_soft"]
        edge = s["bad"] if tone == "bad" else s["warn"]
        d.rounded_rectangle([x0 + 12, top, x1 - 12, top + 58], radius=12,
                            fill=hx(tint))
        d.rounded_rectangle([x0 + 12, top + 9, x0 + 15, top + 49], radius=2,
                            fill=hx(edge))
        d.text((x0 + 26, top + 20), field, font=font(10.5, "mono"),
               fill=hx(edge))
        d.text((x1 - 26, top + 20), sku, font=font(10, "mono"),
               fill=hx(s["faint"]), anchor="ra")
        d.text((x0 + 26, top + 42), code,
               font=font(fit(d, code, "mono", 148, 11), "mono"),
               fill=hx(s["text"]))
    return img


def draw_barcode(img, s, hm, zh):
    x0, y0, x1, y1 = 700, 316, 1380, 516
    img = card(img, (x0, y0, x1, y1), s, radius=22)
    d = ImageDraw.Draw(img)
    d.text((x0 + 24, y0 + 24), "GTIN-14 · 94006381333934",
           font=font(16, "mono_bold"), fill=hx(s["text"]))
    img = pill(img, (x1 - 24, y0 + 12), "mod-10 OK", s, size=11, kind="mono",
               fg=s["good"], bg=s["zone"],
               anchor="ra", padx=12, pady=6, outline=s["good"])
    d = ImageDraw.Draw(img)
    digits = "94006381333934"
    x_start, bw, gap = 733, 41, 3
    weights = ["3" if i % 2 == 0 else "1" for i in range(13)]
    for i, ch in enumerate(digits):
        bx = x_start + i * (bw + gap)
        cx = bx + bw / 2
        if i < 13:
            d.text((cx, y0 + 58), weights[i], font=font(10, "mono"),
                   fill=hx(s["faint"]), anchor="mm")
        fill = s["accent"] if i == 13 else s["zone"]
        edge = s["accent"] if i == 13 else (
            s["good"] if i == 0 else s["zone_edge"])
        d.rounded_rectangle([bx, y0 + 64, bx + bw, y0 + 112], radius=6,
                            fill=hx(fill), outline=hx(edge),
                            width=3 if i in (0, 13) else 1)
        d.text((cx, y0 + 89), ch, font=font(20, "mono"),
               fill=hx(s["on_accent"] if i == 13 else s["text"]),
               anchor="mm")
    d.text((x0 + 24, y0 + 138), hm["bar_note"],
           font=font(fit(d, hm["bar_note"], "cjk" if zh else "en", 340, 13),
                    "cjk" if zh else "en"), fill=hx(s["sub"]))
    d.text((x1 - 24, y0 + 140), hm["bar_meta"],
           font=font(fit(d, hm["bar_meta"], "mono", 252, 11.5), "mono"),
           fill=hx(s["accent"]), anchor="ra")
    d.text((x0 + 24, y0 + 164), hm["bar_note2"],
           font=font(fit(d, hm["bar_note2"], "cjk" if zh else "en", 632, 11.5),
                    "cjk" if zh else "en"), fill=hx(s["sub"]))
    d.text((x0 + 24, y0 + 186), hm["bar_note3"],
           font=font(fit(d, hm["bar_note3"], "cjk" if zh else "en", 632, 11),
                    "cjk" if zh else "en"), fill=hx(s["faint"]))
    return img


def hero(lang, skin_name):
    s = SKIN[skin_name]
    hm = HERO[lang]
    zh = lang == "zh"
    w, h = 1440, 576
    img = gradient(w, h, s["bg_from"], s["bg_to"])
    img = glow(img, 1220, 30, 470, hx(s["accent"]),
               18 if skin_name == "light" else 34)
    img = glow(img, 60, 560, 320, hx(s["accent"]),
               8 if skin_name == "light" else 14)
    img = dot_texture(img, hx(s["dot"]), 10 if skin_name == "light" else 18)

    # ---------------------------------------------------------- left column
    m = 60
    img = pill(img, (m, 52), hm["kicker"], s, size=20 if zh else 19,
               kind="cjk_bold" if zh else "en_bold")
    d = ImageDraw.Draw(img)
    tsize = fit(d, hm["title"], "mono", 620, 84, 54)
    if tsize < 56:
        WARNINGS.append(f"hero.{lang}.title only {tsize}px")
    d.text((m, 126), hm["title"], font=font(tsize, "mono"),
           fill=hx(s["text"]))
    title_bottom = 126 + tsize * 1.16

    vkind = "cjk_bold" if zh else "en_bold"
    vmax = 610
    vsize = 34 if zh else 31
    for line in hm["value"]:
        vsize = min(vsize, fit(d, line, vkind, vmax, vsize, 24))
    vtop = int(max(246, title_bottom + 26))
    for i, line in enumerate(hm["value"]):
        write(img, (m, vtop + i * int(vsize * 1.44)), line, s, vsize, vkind,
              "text", vmax, 24, f"hero.{lang}.value{i}")

    sub_top = vtop + len(hm["value"]) * int(vsize * 1.44) + 7
    write(img, (m + 1, sub_top), hm["sub"], s, 25,
          "cjk" if zh else "en", "sub", 610, 21, f"hero.{lang}.sub")
    meta_top = sub_top + 48
    write(img, (m + 1, meta_top), hm["meta"], s, 20,
          "cjk" if zh else "en", "faint", 610, 17, f"hero.{lang}.meta")

    d = ImageDraw.Draw(img)
    rule_y = meta_top + 58
    d.line([m + 1, rule_y, m + 610, rule_y], fill=hx(s["grid"]), width=2)
    write(img, (m + 1, rule_y + 18), hm["foot"], s, 17,
          "cjk" if zh else "en", "faint", 610, 14,
          f"hero.{lang}.foot")

    # ----------------------------------------------------- right semantic figure
    img = draw_sheet(img, s, hm, zh)
    img = draw_issue_rail(img, s, hm, zh)
    img = draw_barcode(img, s, hm, zh)

    path = os.path.join(OUT, f"dsh-pim-lint-hero-{lang}-{skin_name}.webp")
    img.save(path, "WEBP", quality=92, method=6)
    print(f"wrote dsh-pim-lint-hero-{lang}-{skin_name}.webp")


# ------------------------------------------------------------- flow diagram
FLOW = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8", card="#ffffff",
        edge="#e4e1ee", zone="#f7f4fc", zone_edge="#e5e0f1",
        chip="#ffffff", text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", accent_soft="#ece7f9", good="#16a34a",
        bad="#b42318", bad_soft="#fdf0ee", warn="#b45309",
        warn_soft="#fdf6e8", grid="#e7e4f0", dot="#d9d3ea",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016", card="#1b2231",
        edge="#2e374b", zone="#171e2d", zone_edge="#2a3348",
        chip="#202a44", text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", accent_soft="#242d42", good="#3fb950",
        bad="#f0883e", bad_soft="#33241c", warn="#d9a03c",
        warn_soft="#332a1a", grid="#1e2636", dot="#26314a",
    ),
}

MONO = ("'Consolas','SFMono-Regular','Menlo',ui-monospace,monospace")
SANS = ("'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',"
        "'Segoe UI',sans-serif")


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def tw(text, size, mono=True):
    total = 0.0
    for ch in text:
        if ord(ch) > 0x2E7F:
            total += size
        else:
            total += size * (0.62 if mono else 0.56)
    return total


def T(x, y, body, size, color, family=MONO, weight=None, anchor=None,
      opacity=None, spacing=None):
    attrs = [f'x="{x}"', f'y="{y}"', f'fill="{color}"',
             f'font-family="{family}"', f'font-size="{size}"']
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if anchor:
        attrs.append(f'text-anchor="{anchor}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    if spacing:
        attrs.append(f'letter-spacing="{spacing}"')
    return f'<text {" ".join(attrs)}>{esc(body)}</text>'


def R(x, y, w, h, fill, stroke=None, rx=12, sw=1.4, dash=None,
      opacity=None, extra=""):
    attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"',
             f'rx="{rx}"', f'fill="{fill}"']
    if stroke:
        attrs += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f'<rect {" ".join(attrs)} {extra}/>'


def chip(x, y, w, h, body, s, size=11, fg=None, fill=None, stroke=None,
         family=MONO, weight=None):
    return (R(x, y, w, h, fill or s["chip"], stroke or s["zone_edge"], rx=8,
              sw=1.1)
            + T(x + 8, y + h / 2 + 4, body, size, fg or s["text"],
                family=family, weight=weight))


def flow_svg(skin_name):
    s = FLOW[skin_name]
    dark = skin_name == "dark"
    p = []
    sh_col = "#1b1735" if not dark else "#000000"
    sh_op = "0.10" if not dark else "0.50"

    p.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="660" '
        'viewBox="0 0 1100 660" role="img" aria-labelledby="fig-title fig-desc">')
    p.append('<title id="fig-title">dsh-pim-lint: two channels — whole-table '
             'rule matrix and single-code GS1 probe, one in-memory return'
             '</title>')
    p.append('<desc id="fig-desc">Channel A: catalog.csv goes through a CSV '
             'guard (E_PIM_CSV_EMPTY / E_PIM_HEADER / E_PIM_CSV_ROW throw, '
             'never an issue), then 12 rows enter a 4-field x 7-rule matrix '
             '(SKU required/duplicate, title required, GTIN invalid/'
             'duplicate, price invalid/precision) and produce issues[] as '
             'SKU/field/code. Channel B checks a 14-digit GTIN for format, '
             'packaging indicator and variable measure, and an 18-digit SSCC '
             'for format versus mod-10 checksum. All returns stay in memory: '
             'R0, no file writes, no network, no model call.</desc>')
    p.append(f'''<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0.34" y2="1">
    <stop offset="0" stop-color="{s["bg_from"]}"/>
    <stop offset="1" stop-color="{s["bg_to"]}"/>
  </linearGradient>
  <radialGradient id="halo" cx="0.75" cy="0.05" r="0.7">
    <stop offset="0" stop-color="{s["accent"]}" stop-opacity="{0.16 if dark else 0.10}"/>
    <stop offset="1" stop-color="{s["accent"]}" stop-opacity="0"/>
  </radialGradient>
  <filter id="soft" x="-12%" y="-18%" width="124%" height="142%">
    <feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="{sh_col}" flood-opacity="{sh_op}"/>
  </filter>
  <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.4" markerHeight="6.4" orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10 z" fill="{s["accent"]}"/>
  </marker>
</defs>''')
    p.append(R(0, 0, 1100, 660, "url(#bg)", rx=0))
    p.append(R(0, 0, 1100, 660, "url(#halo)", rx=0))

    # ------------------------------------------------------------- header
    p.append(T(44, 54, "dsh-pim-lint", 28, s["text"], weight="700"))
    p.append(T(44, 84, "整表逐行扫描 ↔ 单码探针：两条通道，同一套 GS1 算术；"
                       "结果只在内存。", 15, s["sub"], family=SANS))
    p.append(R(844, 34, 212, 28, s["accent_soft"], rx=14))
    p.append(T(950, 53, "v0.2.0 · R0 · 本地", 12, s["accent"],
               family=SANS, anchor="middle", weight="700"))
    p.append(f'<line x1="44" y1="104" x2="1056" y2="104" stroke="{s["grid"]}" '
             f'stroke-width="1.4"/>')

    # ------------------------------------------------------- left card A
    p.append(f'<g filter="url(#soft)">{R(44, 116, 700, 384, s["card"], s["edge"], rx=20, sw=1.5)}</g>')
    p.append(T(64, 143, "通道 A · 整表 pim_validate", 13, s["accent"],
               weight="700"))
    p.append(T(724, 143, "rows 12 · issues 8", 11, s["faint"], anchor="end"))

    # input file
    p.append(R(64, 158, 208, 104, s["zone"], s["zone_edge"], rx=14))
    p.append(f'<path d="M80 178h11l5 5v15h-16z" fill="none" stroke="{s["accent"]}" stroke-width="1.6" stroke-linejoin="round"/>')
    p.append(f'<path d="M91 178v5h5" fill="none" stroke="{s["accent"]}" stroke-width="1.6"/>')
    p.append(T(104, 185, "catalog.csv", 14, s["text"], weight="700"))
    p.append(T(80, 208, "UTF-8 · 12 行 × 4 列", 11, s["sub"], family=SANS))
    p.append(f'<line x1="80" y1="216" x2="256" y2="216" stroke="{s["zone_edge"]}" stroke-width="1"/>')
    p.append(T(80, 234, "sku,title,gtin,price", 11, s["accent"]))
    p.append(T(80, 250, "BOM 可省 · 列数须一致", 11, s["faint"], family=SANS))

    # arrows
    p.append(f'<line x1="274" y1="210" x2="306" y2="210" stroke="{s["accent"]}" stroke-width="2.2" marker-end="url(#arr)"/>')

    # CSV guard
    p.append(R(318, 158, 198, 104, s["bad_soft"], s["bad"], rx=14, sw=1.2))
    p.append(f'<circle cx="330" cy="178" r="3.2" fill="{s["bad"]}"/>')
    p.append(T(340, 183, "CSV 守卫", 13, s["text"], family=SANS, weight="700"))
    for i, code in enumerate(("E_PIM_CSV_EMPTY", "E_PIM_HEADER",
                              "E_PIM_CSV_ROW")):
        p.append(T(332, 203 + i * 15, code, 11, s["bad"]))
    p.append(T(332, 251, "硬失败 → throw", 11, s["bad"], family=SANS,
               weight="700"))

    p.append(f'<line x1="518" y1="210" x2="544" y2="210" stroke="{s["accent"]}" stroke-width="2.2" marker-end="url(#arr)"/>')

    # rows chip
    p.append(R(548, 184, 176, 54, s["zone"], s["zone_edge"], rx=12))
    p.append(T(562, 207, "rows[] · 12", 14, s["text"], weight="700"))
    p.append(T(562, 226, "逐行进入检查矩阵", 11, s["sub"], family=SANS))
    p.append(f'<path d="M636 240v28" fill="none" stroke="{s["accent"]}" stroke-width="2.2" marker-end="url(#arr)"/>')

    # rule matrix
    p.append(R(60, 276, 668, 156, s["zone"], s["zone_edge"], rx=16))
    p.append(T(76, 300, "逐行扫描 · 4 字段 × 7 条规则", 12, s["text"],
               family=SANS, weight="700"))
    p.append(T(712, 300, "命中即一条 issue", 11, s["faint"], family=SANS,
               anchor="end"))
    p.append(f'<line x1="76" y1="310" x2="712" y2="310" stroke="{s["zone_edge"]}" stroke-width="1"/>')

    columns = [
        ("sku", [("E_PIM_SKU_REQUIRED", False), ("E_PIM_SKU_DUPLICATE", False)],
         "×1"),
        ("title", [("E_PIM_TITLE_REQUIRED", False), ("仅 1 条规则", True)],
         "×1"),
        ("gtin", [("E_PIM_GTIN_INVALID", False), ("E_PIM_GTIN_DUPLICATE", False)],
         "×4"),
        ("price", [("E_PIM_PRICE_INVALID", False), ("E_PIM_PRICE_PRECISION", False)],
         "×2"),
    ]
    for i, (field, codes, count) in enumerate(columns):
        x = 76 + i * 162
        p.append(T(x, 334, field, 14, s["accent"], weight="700"))
        p.append(T(x + 152, 334, count, 11, s["faint"], anchor="end"))
        for j, (code, placeholder) in enumerate(codes):
            y = 344 + j * 32
            if placeholder:
                p.append(R(x, y, 152, 25, "none", s["zone_edge"], rx=7, sw=1.1,
                           dash="4 4"))
                p.append(T(x + 8, y + 17, code, 11, s["faint"], family=SANS))
            else:
                p.append(R(x, y, 152, 25, s["chip"], s["zone_edge"], rx=7,
                           sw=1.1))
                p.append(f'<line x1="{x + 1.5}" y1="{y + 5}" x2="{x + 1.5}" y2="{y + 20}" stroke="{s["accent"]}" stroke-width="2.4" stroke-linecap="round"/>')
                p.append(T(x + 8, y + 17, code, 11, s["text"]))
    p.append(T(76, 420, "CSV 守卫 3 类错误直接 throw；其余 7 条命中逐行追加 → issues[]",
               11, s["sub"], family=SANS))

    # left result line
    p.append(T(64, 458, "issues[] 8 条 · 例：", 12, s["sub"], family=SANS))
    p.append(T(204, 458, "SKU-1004 / gtin / E_PIM_GTIN_INVALID", 11.5,
               s["accent"]))
    p.append(T(724, 458, "12 行 → 8 条", 11, s["faint"], family=SANS,
               anchor="end"))

    # ------------------------------------------------------- right card B
    p.append(f'<g filter="url(#soft)">{R(756, 116, 300, 384, s["card"], s["edge"], rx=20, sw=1.5)}</g>')
    p.append(T(776, 143, "通道 B · 单码探针", 13, s["accent"], weight="700"))
    p.append(T(1036, 143, "single code", 11, s["faint"], anchor="end"))

    # GTIN bench
    p.append(R(772, 158, 268, 152, s["zone"], s["zone_edge"], rx=14))
    p.append(T(786, 181, "gtin_check · gtin_structure", 11, s["sub"]))
    digits = "94006381333934"
    x0, bw, gap = 786, 16, 1
    for i, ch in enumerate(digits):
        bx = x0 + i * (bw + gap)
        last = i == 13
        p.append(R(bx, 192, bw, 30, s["accent"] if last else s["chip"],
                   s["accent"] if last else s["zone_edge"], rx=4,
                   sw=1.6 if last else 1))
        p.append(T(bx + bw / 2, 212, ch, 11,
                   "#ffffff" if (last and not dark) else (
                       "#0c1016" if last else s["text"]), anchor="middle"))
    p.append(T(786, 246, "3/1 加权 mod-10 · 校验位 4", 11, s["sub"]))
    p.append(T(1024, 246, "OK", 11, s["good"], anchor="end", weight="700"))
    p.append(T(786, 268, "GTIN-14 · indicator 9", 11, s["accent"]))
    p.append(T(786, 286, "variable_measure = true", 11, s["accent"]))

    p.append(f'<line x1="776" y1="322" x2="1036" y2="322" stroke="{s["grid"]}" stroke-width="1"/>')

    # SSCC bench
    p.append(T(776, 346, "pim_sscc_check", 11, s["sub"]))
    p.append(T(776, 372, "340123450000000018", 13, s["text"], weight="700"))
    p.append(T(1036, 372, "× 校验位", 11, s["bad"], family=SANS, anchor="end"))
    p.append(T(776, 394, "剔除空白 → 18 位数字 → mod-10", 11, s["sub"],
               family=SANS))
    p.append(R(776, 404, 192, 25, s["bad_soft"], s["bad"], rx=7, sw=1.2))
    p.append(T(786, 421, "× E_PIM_SSCC_CHECKSUM", 11, s["bad"]))
    p.append(T(776, 452, "格式错 / 校验位错 → 两个 reason", 11, s["faint"],
               family=SANS))
    p.append(T(776, 472, "另一种：格式错 E_PIM_SSCC_FORMAT", 11, s["faint"],
               family=SANS))

    # ------------------------------------------------------- return band
    p.append(f'<g filter="url(#soft)">{R(44, 512, 1012, 116, s["card"], s["edge"], rx=20, sw=1.5)}</g>')
    p.append(T(66, 538, "返回值 · 进程内，不落盘", 12, s["text"],
               family=SANS, weight="700"))
    p.append(T(1034, 538, "R0 · 无网络 · 无模型", 11, s["faint"],
               family=SANS, anchor="end"))

    # A
    p.append(R(64, 550, 318, 62, s["zone"], s["zone_edge"], rx=12))
    p.append(T(78, 570, "pim_validate", 13, s["accent"], weight="700"))
    p.append(T(78, 591, "{ rows, issues[] }", 12, s["text"]))
    p.append(T(370, 591, "12 / 8", 11, s["good"], anchor="end"))
    # B
    p.append(R(394, 550, 448, 62, s["zone"], s["zone_edge"], rx=12))
    p.append(T(408, 570, "pim_gtin_check   → { gtin, valid }", 11.5,
               s["accent"]))
    p.append(T(408, 591, "pim_gtin_structure → { format, indicator?, "
                        "variable_measure }", 11, s["sub"]))
    # C
    p.append(R(854, 550, 188, 62, s["zone"], s["zone_edge"], rx=12))
    p.append(T(868, 570, "pim_sscc_check", 13, s["accent"], weight="700"))
    p.append(T(868, 591, "{ sscc, valid, reason? }", 11, s["sub"]))

    # ------------------------------------------------------------- footer
    p.append(T(44, 650, "GTIN-14 首位：0 基础 · 1–8 包装 · 9 变度量 · "
                        "SSCC 18 位先剔空白 · R0 全程不写文件", 11.5,
               s["sub"], family=SANS))
    p.append(T(1056, 650, "12 行样例 → 8 条问题", 11, s["faint"], family=SANS,
               anchor="end"))
    p.append('</svg>')
    return "\n".join(p) + "\n"


def main():
    os.makedirs(OUT, exist_ok=True)
    for lang in ("zh", "en"):
        for skin in ("light", "dark"):
            hero(lang, skin)
    for skin in ("light", "dark"):
        with open(os.path.join(OUT, f"dsh-pim-lint-flow-v5-{skin}.svg"),
                  "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
        print(f"wrote dsh-pim-lint-flow-v5-{skin}.svg")
    if WARNINGS:
        print("\n".join(WARNINGS))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
