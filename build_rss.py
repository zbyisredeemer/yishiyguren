import os, re, glob, subprocess, html, datetime

BASE_URL = "https://zbyisredeemer.github.io/yishiyguren"
FEED_PATH = "feed.xml"
SHOW_TITLE = "一诗一古人"
SHOW_DESC = "诗词人物生平播客。每日一人，从少年讲到终老——名篇开篇，生平节点，隔千年对谈。"
AUTHOR = "一诗一古人"
EP_DIR = "episodes"

def mp3_len(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return int(float(r.stdout.strip()))

def rfc822(ts):
    return datetime.datetime.utcfromtimestamp(ts).strftime("%a, %d %b %Y %H:%M:%S +0000")

def read_shownotes_meta(path):
    if not os.path.exists(path):
        return None
    txt = open(path, encoding="utf-8").read()
    title = ""
    for l in txt.split("\n"):
        if l.startswith("# "):
            title = l[2:].strip()
            break
    return title

items = []
for ep in sorted(glob.glob(os.path.join(EP_DIR, "[0-9]*_*"))):
    mp3 = os.path.join(ep, "01.mp3")
    if not os.path.exists(mp3):
        continue
    num = os.path.basename(ep)[:3]
    poet = os.path.basename(ep).split("_", 1)[1]
    sn = read_shownotes_meta(os.path.join(ep, "shownotes.md"))
    title = sn or f"{num}｜{poet}"
    sn_body = ""
    if os.path.exists(os.path.join(ep, "shownotes.md")):
        sn_body = open(os.path.join(ep, "shownotes.md"), encoding="utf-8").read()
        sn_body = re.sub(r"^#.*$", "", sn_body, flags=re.M).strip()[:2000]
    cover = f"covers/{os.path.basename(ep).lower().replace('李白','libai').replace('杜甫','dufu')}.jpg"
    cover_map = {}
    for c in glob.glob("covers/*.jpg"):
        cover_map[os.path.splitext(os.path.basename(c))[0]] = c
    cover_rel = ""
    for k, v in cover_map.items():
        if k.startswith(num):
            cover_rel = v
    mtime = os.path.getmtime(mp3)
    items.append({
        "num": num, "poet": poet, "title": title, "desc": sn_body,
        "mp3": mp3, "len": os.path.getsize(mp3), "dur": mp3_len(mp3),
        "mtime": mtime, "cover": cover_rel,
    })

items.sort(key=lambda x: x["num"])

xml = []
xml.append('<?xml version="1.0" encoding="UTF-8"?>')
xml.append('<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:content="http://purl.org/rss/1.0/modules/content/" version="2.0">')
xml.append("<channel>")
xml.append(f"<title>{SHOW_TITLE}</title>")
xml.append(f"<link>{BASE_URL}</link>")
xml.append("<language>zh-cn</language>")
xml.append(f"<description>{SHOW_DESC}</description>")
xml.append(f"<itunes:author>{AUTHOR}</itunes:author>")
xml.append('<itunes:category text="History"><itunes:category text="Society &amp; Culture"/></itunes:category>')
xml.append(f'<itunes:image href="{BASE_URL}/covers/show_cover.jpg"/>')
xml.append(f"<itunes:explicit>false</itunes:explicit>")
xml.append(f"<lastBuildDate>{rfc822(datetime.datetime.now(datetime.timezone.utc).timestamp())}</lastBuildDate>")

for it in items:
    xml.append("<item>")
    xml.append(f"<title>{html.escape(it['title'])}</title>")
    xml.append(f'<enclosure url="{BASE_URL}/{it["mp3"]}" length="{it["len"]}" type="audio/mpeg"/>')
    xml.append(f'<guid isPermaLink="false">{SHOW_TITLE}-ep{it["num"]}</guid>')
    xml.append(f"<pubDate>{rfc822(it['mtime'])}</pubDate>")
    xml.append(f'<itunes:duration>{it["dur"]}</itunes:duration>')
    xml.append(f'<itunes:episode>{int(it["num"])}</itunes:episode>')
    xml.append(f'<itunes:episodeType>full</itunes:episodeType>')
    if it["cover"]:
        xml.append(f'<itunes:image href="{BASE_URL}/{it["cover"]}"/>')
    desc = html.escape(it["desc"]) if it["desc"] else html.escape(it["title"])
    xml.append(f'<description><![CDATA[{it["desc"]}]]></description>')
    xml.append("</item>")

xml.append("</channel>")
xml.append("</rss>")

open(FEED_PATH, "w", encoding="utf-8").write("\n".join(xml))
print(f"{FEED_PATH} 生成完成，{len(items)} 期")
for it in items:
    print(f"  ep{it['num']} {it['poet']} {it['dur']//60}:{it['dur']%60:02d}")
