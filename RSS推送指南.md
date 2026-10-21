# 通过 RSS 接口推送到小宇宙

## 结论

- **小宇宙没有开放创作者上传 API**，官方入口只有 App 内「创作中心」人工上传，带内容审核，无法脚本化。
- 播客行业事实标准的"接口"是 **RSS**：小宇宙支持收录外部 RSS 地址。**收录只需人工提交一次**，之后每期的"推送"只是更新 feed 文件，小宇宙定时抓取——这才是可自动化的部分。
- 同一份 feed 之后还能原样提交给 Apple Podcasts、Spotify 等平台，一份素材全网分发。

## 本项目的部署状态（已落地）

| 项 | 值 |
|---|---|
| GitHub 仓库 | https://github.com/zbyisredeemer/yishiyguren |
| 线上 feed（提交给小宇宙的地址） | **https://zbyisredeemer.github.io/yishiyguren/feed.xml** |
| 托管方式 | GitHub Pages（main 分支根目录，免费） |

仓库内文件：`feed.xml`、`covers/`（封面）、`episodes/*/01.mp3`（音频）、`*.py` / `deploy.sh`（工具链）。

## 三步走通

### 第 1 步：托管 —— 已完成

GitHub Pages 已开启并验证：feed.xml 与 001 音频线上均返回 200。
（沙箱环境下 git push 的 HTTPS/SSH 通道均被限制，实际推送走 GitHub REST API，见 `gh_push.py`。）

### 第 2 步：提交给小宇宙（一次性人工操作）

1. 小宇宙 App → 创作中心，或在节目主页点「联系小宇宙」
2. 提交 feed 地址：`https://zbyisredeemer.github.io/yishiyguren/feed.xml`
3. 审核通常几个工作日；已有 2 期存量，建议再攒 2-3 期（自动化每天 8 点产出）后提交，通过率更高

### 第 3 步：之后的每期"推送"

每日自动产出完成后，跑：

```bash
./deploy.sh
```

它依次做三件事：重新生成 `feed.xml` → 本地 git 提交 → `gh_push.py` 通过 API 推送到 GitHub。推送后小宇宙定时抓取（几分钟到一天），新集自动上线，无需任何人工上传。

## 注意事项

- GitHub Pages 单库建议 <1GB、单文件 <100MB：每集约 10MB，够用约 100 期；之后可平移到国内 OSS（迁移只需改 `build_rss.py` 的 `BASE_URL`）
- feed 是公开的：任何拿到地址的人都能看到全部音频与 shownotes（本节目无敏感内容，公开是播客分发的必要条件）
- 不要往仓库提交 `.workbuddy-ai/`（已在 .gitignore 和 gh_push.py 的跳过清单中）
