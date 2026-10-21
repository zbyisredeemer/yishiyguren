import base64, hashlib, json, os, subprocess, sys, urllib.request, urllib.error, datetime

REPO = "zbyisredeemer/yishiyguren"
ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {".git", ".workbuddy-ai", "__pycache__", "voices"}
SKIP_FILES = {".DS_Store"}

def gh_token():
    r = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("gh auth token 失败")
    return r.stdout.strip()

TOKEN = gh_token()

def api(method, path, data=None):
    req = urllib.request.Request("https://api.github.com/repos/%s/%s" % (REPO, path), method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, body) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        print("API ERROR", method, path, e.code, e.read()[:300])
        raise

def blob_sha(content):
    h = hashlib.sha1()
    h.update(("blob %d\0" % len(content)).encode())
    h.update(content)
    return h.hexdigest()

def local_files():
    out = {}
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            if fn in SKIP_FILES:
                continue
            p = os.path.join(dp, fn)
            out[os.path.relpath(p, ROOT)] = open(p, "rb").read()
    return out

files = local_files()

try:
    ref = api("GET", "git/ref/heads/main")
    commit_sha = ref["object"]["sha"]
    commit = api("GET", "git/commits/" + commit_sha)
    tree_sha = commit["tree"]["sha"]
    remote_tree = api("GET", "git/trees/%s?recursive=1" % tree_sha)
    remote = {t["path"]: t["sha"] for t in remote_tree.get("tree", []) if t["type"] == "blob"}
except urllib.error.HTTPError:
    print("空仓库，先用 Contents API 引导首个提交")
    boot = "README.md" if "README.md" in files else sorted(files)[0]
    r = api("PUT", "contents/" + boot.replace(" ", "%20"), {
        "message": "init: " + boot,
        "content": base64.b64encode(files[boot]).decode(),
    })
    commit_sha = r["commit"]["sha"]
    commit = api("GET", "git/commits/" + commit_sha)
    tree_sha = commit["tree"]["sha"]
    remote_tree = api("GET", "git/trees/%s?recursive=1" % tree_sha)
    remote = {t["path"]: t["sha"] for t in remote_tree.get("tree", []) if t["type"] == "blob"}

changed = {p: c for p, c in files.items() if remote.get(p) != blob_sha(c)}
if not changed:
    print("远端已是最新，无变更")
    sys.exit(0)

print("待推送 %d 个文件：" % len(changed))
for p in sorted(changed):
    print("  ", p)

entries = []
for p, content in changed.items():
    blob = api("POST", "git/blobs", {"content": base64.b64encode(content).decode(), "encoding": "base64"})
    entries.append({"path": p, "mode": "100644", "type": "blob", "sha": blob["sha"]})

tree_data = {"tree": entries}
if tree_sha:
    tree_data["base_tree"] = tree_sha
tree = api("POST", "git/trees", tree_data)

msg = "update: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
commit_data = {"message": msg, "tree": tree["sha"]}
if commit_sha:
    commit_data["parents"] = [commit_sha]
new_commit = api("POST", "git/commits", commit_data)

if commit_sha:
    api("PATCH", "git/refs/heads/main", {"sha": new_commit["sha"]})
else:
    api("POST", "git/refs", {"ref": "refs/heads/main", "sha": new_commit["sha"]})

print("已推送:", new_commit["html_url"])
