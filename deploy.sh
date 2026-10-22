#!/bin/bash
set -e
cd "$(dirname "$0")"
PY=/Users/zhangyusheng/.workbuddy-ai/binaries/python/envs/default/bin/python3
$PY build_rss.py
git add -A 2>/dev/null || true
git diff --cached --quiet 2>/dev/null || git commit -m "update: $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || true
$PY gh_push.py
