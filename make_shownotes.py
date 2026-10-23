import re, subprocess, os

CFG = {
    "episodes/001_李白": {
        "couple": "天上谪仙人，人间李太白",
        "intro": "国民度最高的诗人，用一生回答了'天生我材必有用'。从蜀中少年到长安翰林，从嵩山酒宴到夜郎孤舟，二十多分钟陪他走完这一生——狂到天上，也低到泥土里。",
        "profile": [("姓名", "李白，字太白，号青莲居士"), ("生卒", "701-762，唐代"), ("籍贯", "蜀中绵州昌隆（今四川江油），自认蜀人"), ("身份", "诗人、道士，曾供奉翰林")],
        "next": "第 2 期｜杜甫：把时代扛在肩上的人",
    },
    "episodes/002_杜甫": {
        "couple": "安得广厦千万间，大庇天下寒士俱欢颜",
        "intro": "他被称作'诗圣'，却一生颠沛：少年壮游、洛阳初见、困守长安、国破山河、辞官西行、草堂秋风、夔州绝唱——七个节点看完一个把时代扛在肩上的人。听懂杜甫，才算听懂唐朝的另一半。",
        "profile": [("姓名", "杜甫，字子美，自号少陵野老"), ("生卒", "712-770，唐代"), ("籍贯", "祖籍京兆杜陵（今陕西西安），生于巩县（今河南巩义）"), ("身份", "诗人，世称'诗圣'，其诗被称为'诗史'")],
        "next": "第 3 期｜王维：前半生庙堂，后半空山",
    },
    "episodes/003_王维": {
        "couple": "行到水穷处，坐看云起时",
        "intro": "前半生庙堂、后半生空山的'诗佛'：少年早慧、济州贬谪、张九龄提携、大漠孤烟、辋川烟雨、陷贼晚节——二十多分钟，看一个最有佛缘却最放不下功名的人，怎么把'干净'活到底。",
        "profile": [("姓名", "王维，字摩诘"), ("生卒", "701-761，唐代"), ("籍贯", "太原祁县（今山西祁县）人，家居蒲州（今山西永济）"), ("身份", "诗人、画家、音乐家，世称'诗佛'，官至尚书右丞")],
        "next": "第 4 期｜孟浩然：让李白低头的布衣诗人",
    },
    "episodes/004_孟浩然": {
        "couple": "春眠不觉晓，处处闻啼鸟",
        "intro": "让李白低头的一代布衣：鹿门少年、长安失意、吴越漫游、张九龄幕府、食鲜而终——二十多分钟，看一个没卷赢的好人，怎么把一生过成'语淡味厚'四个字。读懂孟浩然，就读懂失意与和解。",
        "profile": [("姓名", "孟浩然，名浩，字浩然，世称孟山人"), ("生卒", "689-740，唐代"), ("籍贯", "襄州襄阳（今湖北襄阳）人"), ("身份", "诗人，唐代山水田园诗派开创者，与王维并称'王孟'，终身未仕")],
        "next": "第 5 期｜屈原：中国诗歌源头的人",
    },
}

def cjk(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def mmss(s):
    return f"{int(s//60):02d}:{int(s%60):02d}"

for ep, cfg in CFG.items():
    script = open(os.path.join(ep, "script.md"), encoding="utf-8").read()
    audio = os.path.join(ep, "01.mp3")
    total = dur(audio)
    lines = [l for l in script.split("\n") if l.strip() and not l.startswith("#")]
    body = "\n".join(lines)

    sections = []
    cur = None
    for l in script.split("\n"):
        if l.startswith("## "):
            if cur: sections.append(cur)
            cur = {"name": l[3:].strip(), "text": ""}
        elif cur is not None:
            cur["text"] += l + "\n"
    if cur: sections.append(cur)

    total_chars = sum(cjk(s["text"]) for s in sections)
    acc = 0
    rows = []
    for s in sections:
        start = acc / total_chars * total
        acc += cjk(s["text"])
        rows.append((mmss(start), s["name"], cjk(s["text"])))

    poem = ""
    for s in sections:
        if "朗读" in s["name"]:
            poem = re.sub(r"\n{2,}", "\n", s["text"].strip())

    md = []
    md.append(f"# {os.path.basename(ep).split('_')[0]}｜{cfg['couple']}\n")
    md.append(f"> {cfg['intro']}\n")
    md.append("## 章节时间轴\n")
    for t, name, _ in rows:
        md.append(f"- {t}  {name}")
    md.append("\n## 本期名篇\n")
    md.append(poem + "\n")
    md.append("## 人物小档案\n")
    for k, v in cfg["profile"]:
        md.append(f"- **{k}**：{v}")
    md.append(f"\n---\n完整逐字稿见评论区置顶。\n下一期：{cfg['next']}\n")
    md.append("\n《一诗一古人》——每日一人，从少年讲到终老。\n")

    out = os.path.join(ep, "shownotes.md")
    open(out, "w", encoding="utf-8").write("\n".join(md))
    print(out, f"音频 {mmss(total)}，{len(sections)} 个章节")
    for t, name, c in rows:
        print("  ", t, name, c)
