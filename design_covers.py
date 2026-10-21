import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SONG = "/System/Library/Fonts/Supplemental/Songti.ttc"

def kai(size):
    return ImageFont.truetype(SONG, size, index=1)

def song(size):
    return ImageFont.truetype(SONG, size, index=6)
W = H = 2000
PAPER = (244, 238, 225)
INK = (38, 34, 28)
INK_SOFT = (90, 84, 72)
SEAL = (166, 59, 42)

def paper(w=W, h=H):
    img = Image.new("RGB", (w, h), PAPER)
    noise = Image.effect_noise((w, h), 14).convert("RGBA")
    img = Image.blend(img.convert("RGBA"), noise, 0.05).convert("RGB")
    return img

def moon(img, cx, cy, r, color=(216, 208, 186)):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i, a in zip(range(r, 0, -3), range(10, 210, 6)):
        d.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color + (a,))
    img.alpha_composite(ov)

def ridge(img, base, amp, color, alpha, phase=0.0, freq=0.0016):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    pts = []
    for x in range(0, W + 20, 10):
        y = base + amp * math.sin(x * freq + phase) + amp * 0.5 * math.sin(x * freq * 2.7 + phase * 1.7)
        pts.append((x, y))
    pts += [(W, H), (0, H)]
    d.polygon(pts, fill=color + (alpha,))
    img.alpha_composite(ov)

def seal(img, cx, cy, size, char, color=SEAL):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle([cx - size // 2, cy - size // 2, cx + size // 2, cy + size // 2],
                        radius=int(size * 0.12), fill=color + (235,))
    f = song(int(size * 0.72))
    bbox = d.textbbox((0, 0), char, font=f)
    d.text((cx - (bbox[2] - bbox[0]) / 2 - bbox[0], cy - (bbox[3] - bbox[1]) / 2 - bbox[1]),
           char, font=f, fill=(250, 246, 238, 255))
    img.alpha_composite(ov)

def text_v(img, x, y, text, font, fill, spacing=1.12):
    d = ImageDraw.Draw(img)
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        bbox = font.getbbox(ch)
        y += int((bbox[3] - bbox[1]) * spacing) + int(font.size * 0.18)

def show_cover():
    img = paper().convert("RGBA")
    moon(img, 1620, 430, 260)
    ridge(img, 1430, 130, (60, 56, 48), 46, phase=0.6)
    ridge(img, 1610, 150, (60, 56, 48), 90, phase=2.4)
    ridge(img, 1810, 110, (40, 37, 32), 170, phase=4.2)
    text_v(img, 620, 300, "一诗一古人", kai(168), INK)
    seal(img, 1010, 1150, 132, "诗")
    d = ImageDraw.Draw(img)
    d.text((950, 1265), "每日一人 · 从少年讲到终老", font=song(44), fill=INK_SOFT)
    d.text((950, 1345), "诗词人物生平播客", font=song(36), fill=(140, 132, 116))
    img.convert("RGB").save("covers/show_cover.jpg", quality=92)

def episode_cover(fname, poet, tag, poem_line, seal_char, seed):
    img = paper().convert("RGBA")
    rnd = random.Random(seed)
    moon(img, 1560, 400, 230)
    ridge(img, 1450, 120, (60, 56, 48), 40, phase=seed * 0.7)
    ridge(img, 1620, 140, (60, 56, 48), 80, phase=seed * 1.3 + 1.0)
    ridge(img, 1820, 100, (40, 37, 32), 160, phase=seed * 1.9 + 2.0)
    d = ImageDraw.Draw(img)
    ghost = kai(940)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(ov)
    gd.text((960, 580), seal_char, font=ghost, fill=(60, 56, 48, 26))
    img.alpha_composite(ov)
    d.text((170, 210), tag, font=song(46), fill=(140, 132, 116))
    d.text((170, 300), poet, font=kai(190), fill=INK)
    text_v(img, 1690, 300, poem_line, kai(62), INK_SOFT, spacing=1.28)
    seal(img, 320, 1250, 128, seal_char)
    d.text((170, 1350), "《一诗一古人》第 %s 期" % tag.replace("第 ", "").replace(" 期", ""), font=song(40), fill=(140, 132, 116))
    img.convert("RGB").save("covers/%s.jpg" % fname, quality=92)

import os, sys
os.makedirs("covers", exist_ok=True)
if len(sys.argv) >= 6:
    num, poet, tag, line, seal_char, seed = sys.argv[1:7]
    episode_cover("%s_%s" % (num, poet), poet, tag, line, seal_char, int(seed))
    print("cover done: covers/%s_%s.jpg" % (num, poet))
else:
    show_cover()
    episode_cover("001_libai", "李白", "第 1 期", "君不见黄河之水天上来", "白", 11)
    episode_cover("002_dufu", "杜甫", "第 2 期", "国破山河在", "杜", 23)
    print("done")
