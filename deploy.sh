#!/bin/bash
set -e
cd "$(dirname "$0")"
PY=/Users/zhangyusheng/.workbuddy-ai/binaries/python/envs/default/bin/python3
$PY build_rss.py
git add -A 2>/dev/null || true
git diff --cached --quiet 2>/dev/null || git commit -m "update: $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || true
# 首选 git HTTPS 推送（大文件稳定）：token 走 basic auth header，勿放 URL（会被代理拦截）
TOKEN=$(gh auth token)
BASIC=$(printf 'x-access-token:%s' "$TOKEN" | base64)
if git -c http.extraHeader="Authorization: Basic $BASIC" push https://github.com/zbyisredeemer/yishiyguren.git main; then
  echo "git push 成功"
else
  echo "git push 失败，回退 gh_push.py API 通道"
  $PY gh_push.py
fi
