# 通过 RSS 接口推送到小宇宙

## 先说结论

- **小宇宙没有开放创作者上传 API**。官方唯一入口是 App 内「创作中心」人工上传，带内容审核，无法脚本化。
- 播客行业事实标准的"接口"是 **RSS**：小宇宙支持收录外部 RSS 地址。**收录只需人工提交一次**，之后每期的"推送"只是更新 feed 文件，小宇宙定时抓取——这才是可自动化的部分。
- 同一份 feed 之后还能原样提交给 Apple Podcasts、Spotify 等海外平台，一份素材全网分发。

## 三步走通

### 第 1 步：托管（把 feed 和音频变成公网 URL）

| 方案 | 费用 | 说明 |
|---|---|---|
| GitHub Pages / Cloudflare Pages | 免费 | 需要 GitHub 账号；国内访问偏慢但小宇宙抓取可用，是独立播客最常用方案 |
| 自有域名 + 阿里云 OSS / 腾讯云 COS | 低 | 国内速度快，但域名需 ICP 备案 |
| Firstory / Anchor（Spotify for Podcasters） | 免费 | 平台自动生成 RSS，其后台有一键申请分发到各平台的流程 |

需要公开的文件：`feed.xml`、`covers/`（全部封面）、`episodes/*/01.mp3`（音频）。

### 第 2 步：提交（一次性人工操作）

1. 改 `build_rss.py` 顶部的 `BASE_URL` 为你的托管地址，运行 `python3 build_rss.py` 生成 feed.xml，随其他文件一起部署
2. 小宇宙 App → 创作中心，或在节目主页点「联系小宇宙」，提交 feed.xml 的公开 URL
3. 审核通常几个工作日；建议提交时已有 3-5 期存量审核更稳、通过更快

### 第 3 步：之后的每期"推送"

```
跑每日自动产出（script + 01.mp3 + 封面 + shownotes）
        ↓
python3 build_rss.py        # feed.xml 自动加入新一期
        ↓
部署到托管（git push 或上传） # 小宇宙定时抓取，无需再人工上传
```

小宇宙抓取间隔通常几分钟到一天，新集自动出现，shownotes/封面随 feed 一起更新。

## 本项目文件

- `build_rss.py` — 扫描 episodes/ 自动生成含 iTunes 标签的标准 podcast feed（标题、时长、单集封面、shownotes 全带上）
- `feed.xml` — 生成的 feed（BASE_URL 改成真实地址后重新生成）

选定托管方案后告诉我，我把 `build_rss.py` 也加进每日自动任务，实现"每天产出 → feed 更新 → 部署"全自动，你只需审核内容。
