# -*- coding: utf-8 -*-
"""生成小红书图文笔记 5 张竖图（封面 + 4 页），可直接上传。"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1440
WHITE = (255, 255, 255)
RED = (228, 0, 43)       # 麦当劳红
YELLOW = (255, 199, 44)  # 麦当劳黄
DARK = (26, 26, 26)
GRAY = (120, 120, 120)
LIGHT = (245, 245, 245)

SIMHEI = "C:/Windows/Fonts/simhei.ttf"
MSYH = "C:/Windows/Fonts/msyh.ttc"  # index 0


def font(size, bold=True):
    path = SIMHEI if bold else MSYH
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_w):
    """按字符宽度换行（适配中文）。"""
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur)
            cur = ""
            continue
        test = cur + ch
        if fnt.getlength(test) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def draw_text_center(d, xy, text, fnt, fill, anchor="mm"):
    d.text(xy, text, font=fnt, fill=fill, anchor=anchor)


def render_slide(title, blocks, out_path, top_label=None):
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    x = 80
    y = 170 if top_label else 110

    # 顶部色带 + 标签
    if top_label:
        d.rounded_rectangle([40, 50, W - 40, 50 + 90], radius=20, fill=RED)
        draw_text_center(d, (W // 2, 95), top_label, font(44), WHITE)

    # 标题
    if title:
        for ln in wrap(title, font(66), W - 2 * x):
            d.text((x, y), ln, font=font(66), fill=DARK)
            y += 86
        y += 20

    for b in blocks:
        kind = b.get("type", "text")
        if kind == "text":
            size = b.get("size", 40)
            fill = b.get("fill", DARK)
            for ln in wrap(b["text"], font(size), W - 2 * x):
                d.text((x, y), ln, font=font(size), fill=fill)
                y += size + 14
            y += 10
        elif kind == "highlight":
            size = b.get("size", 72)
            box_h = size + 56
            d.rounded_rectangle([x, y, W - x, y + box_h], radius=24, fill=YELLOW)
            draw_text_center(d, (W // 2, y + box_h // 2), b["text"], font(size), DARK)
            y += box_h + 30
        elif kind == "quote":
            size = b.get("size", 40)
            pad = 24
            lines = wrap(b["text"], font(size), W - 2 * x - 2 * pad)
            box_h = len(lines) * (size + 12) + 2 * pad
            d.rounded_rectangle([x, y, W - x, y + box_h], radius=20, fill=LIGHT,
                                outline=RED, width=3)
            ty = y + pad
            for ln in lines:
                d.text((x + pad, ty), ln, font=font(size), fill=DARK)
                ty += size + 12
            y += box_h + 30
        elif kind == "chips":
            size = b.get("size", 38)
            items = b["items"]
            chip_h = size + 30
            cx = x
            for it in items:
                tw = font(size).getlength(it) + 44
                if cx + tw > W - x:
                    cx = x
                    y += chip_h + 16
                d.rounded_rectangle([cx, y, cx + tw, y + chip_h], radius=chip_h // 2,
                                    fill=RED)
                draw_text_center(d, (cx + tw // 2, y + chip_h // 2), it, font(size), WHITE)
                cx += tw + 16
            y += chip_h + 30
        elif kind == "rows":
            size = b.get("size", 36)
            for row in b["rows"]:
                row_h = 150
                d.rounded_rectangle([x, y, W - x, y + row_h], radius=18, fill=LIGHT)
                d.rounded_rectangle([x, y, x + 120, y + row_h], radius=18, fill=RED)
                draw_text_center(d, (x + 60, y + row_h // 2), row["rank"], font(56), WHITE)
                tx = x + 150
                ty = y + 24
                d.text((tx, ty), row["name"], font=font(40), fill=DARK)
                ty += 52
                d.text((tx, ty), row["macro"], font=font(34), fill=GRAY)
                ty += 48
                d.text((tx, ty), row["price"], font=font(34), fill=RED)
                y += row_h + 18
            y += 10
        elif kind == "footer":
            size = b.get("size", 32)
            d.line([x, y, W - x, y], fill=(220, 220, 220), width=2)
            y += 24
            for ln in wrap(b["text"], font(size), W - 2 * x):
                d.text((x, y), ln, font=font(size), fill=GRAY)
                y += size + 10

    img.save(out_path, "PNG")
    print("saved", out_path)


OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "xhs")
os.makedirs(OUT, exist_ok=True)

# 1. 封面
render_slide(
    "减脂期麦当劳\n怎么吃？",
    [
        {"type": "highlight", "text": "500 大卡 + 省 11 块", "size": 76},
        {"type": "text", "text": "程序员用 AI 算出来的，不是瞎编的", "size": 40, "fill": GRAY},
        {"type": "footer", "text": "开源地址见评论区 ★  项目：mcd-macro-buddy"},
    ],
    os.path.join(OUT, "01_cover.png"),
    top_label="麦麦热量精算师",
)

# 2. 痛点
render_slide(
    "谁懂啊  优惠券算到裂开",
    [
        {"type": "chips", "items": ["麦麦省", "我的券", "门店券", "月活动"], "size": 40},
        {"type": "text", "text": "一个写代码的人，", "size": 42},
        {"type": "text", "text": "居然算不清今天该花多少。", "size": 42},
    ],
    os.path.join(OUT, "02_pain.png"),
    top_label="痛点",
)

# 3. 反转
render_slide(
    "不服！回家写了个 AI 饭搭子",
    [
        {"type": "text", "text": "跟它说一句：", "size": 42},
        {"type": "quote", "text": "减脂午餐 不超 550 大卡 蛋白尽量高 预算 30", "size": 44},
        {"type": "text", "text": "它直接甩出 Top3 方案 ↓", "size": 42, "fill": RED},
    ],
    os.path.join(OUT, "03_turn.png"),
    top_label="反转",
)

# 4. 数据
render_slide(
    "真算的，不是编的",
    [
        {"type": "rows", "size": 36, "rows": [
            {"rank": "1", "name": "板烧鸡腿堡 + 玉米杯", "macro": "500 大卡 · 29g 蛋白",
             "price": "原价 31.5 → 实付 20.5  省 11"},
            {"rank": "2", "name": "单点板烧鸡腿堡", "macro": "430 大卡 · 26g 蛋白",
             "price": "实付 22.0"},
            {"rank": "3", "name": "板烧 + 无糖可乐", "macro": "430 大卡 · 26g 蛋白",
             "price": "实付 23.0  省 8"},
        ]},
        {"type": "footer", "text": "价格 / 优惠均为麦当劳官方实时数据，非脑补。"},
    ],
    os.path.join(OUT, "04_data.png"),
    top_label="方案",
)

# 5. 行动
render_slide(
    "已经开源啦",
    [
        {"type": "text", "text": "地址在评论区第一条，往下滑", "size": 42},
        {"type": "text", "text": "麦当劳开发者大赛按 Star 排名，冲榜中", "size": 42, "fill": RED},
        {"type": "text", "text": "宝子们觉得有用，帮我点个 Star 呗 ★", "size": 42},
        {"type": "footer", "text": "#减脂 #麦当劳 #AI #程序员 #控卡 #省钱 #健身餐"},
    ],
    os.path.join(OUT, "05_cta.png"),
    top_label="求 Star",
)

print("ALL DONE")
