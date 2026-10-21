#!/bin/bash
set -e
cd "$(dirname "$0")"
PY=/Users/zhangyusheng/.workbuddy-ai/binaries/python/envs/default/bin/python3
$PY build_rss.py
git add -A
if git diff --cached --quiet; then
  echo "无变更，跳过提交"
else
  git commit -m "update: $(date '+%Y-%m-%d %H:%M')"
  git push origin main
  echo "已推送，小宇宙将定时抓取"
fi
