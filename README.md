# 一诗一古人

诗词人物生平播客。每日一人，从少年讲到终老——名篇开篇，生平节点，夹叙夹议。

## 站点用途

本站是节目的 RSS 源与音频托管：

- `feed.xml` — podcast RSS（已提交小宇宙，Apple Podcasts / Spotify 可同源分发）
- `episodes/<序号>_<人物>/01.mp3` — 每期音频（`script.md` 为逐字稿，`shownotes.md` 为节目简介）
- `covers/` — 节目主封面与各期单集封面

## 本地工具

- `build_rss.py` — 扫描 episodes/ 重新生成 feed.xml
- `design_covers.py` — 生成封面（无参数重建主封面；带参生成新单集封面）
- `make_shownotes.py` — 生成 shownotes（含章节时间轴）
- `deploy.sh` — 重新生成 feed 并推送部署
