#!/usr/bin/env python3
"""Rebuild v-fanuzpbo/previews/ from pages.json. Run from anywhere: python3 v-fanuzpbo/tools/make_previews.py
Copies each page as it exists on a stage's git ref (see "stages" in pages.json), marks it as a preview,
strips tracking and redirect scripts, neuters links. Re-run after a release branch changes."""
import os, re, json, shutil, subprocess, html
V = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); REPO = os.path.dirname(V)
P = V + "/previews"
cfg = json.load(open(V + "/pages.json"))
def _resolve(ref):  # fresh clones only have origin/<branch>; use it when no local branch exists
    if subprocess.run(["git", "rev-parse", "--verify", "-q", ref], cwd=REPO, capture_output=True).returncode == 0: return ref
    return "origin/" + ref
for _st in cfg["stages"].values(): _st["ref"] = _resolve(_st["ref"])
def git(*a, raw=False):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=not raw); return r
def show(ref, path):
    r = git("show", f"{ref}:{path}"); return r.stdout if r.returncode == 0 else None
main_assets = set(git("ls-tree", "-r", "--name-only", "main", "assets").stdout.split())
def wrap(h, label, ph):
    # assets only on a release branch live in previews/assets
    for n in set(re.findall(r'/(assets/[A-Za-z0-9_.\-]+)', h)):
        if n not in main_assets: h = h.replace("/" + n, "/v-fanuzpbo/previews/" + n)
    h = re.sub(r'<script[^>]*pixel\.js[^>]*></script>', '', h)
    # silent previews: no scripts (players, tracking), no media or embeds, no autoplay
    h = re.sub(r'<script\b.*?</script>', '', h, flags=re.S | re.I)
    h = re.sub(r'<(audio|video|iframe|object|embed)\b.*?</\1>', '', h, flags=re.S | re.I)
    h = re.sub(r'<(audio|video|iframe|embed|source)\b[^>]*/?>', '', h, flags=re.I)
    h = re.sub(r'\sautoplay(=("[^"]*"|\'[^\']*\'))?', '', h, flags=re.I)
    h = re.sub(r'<script>\s*/\* Before release.*?</script>', '', h, flags=re.S)
    h = re.sub(r'href="/[^"]*"', lambda m: m.group(0) if m.group(0).startswith('href="/assets/') else 'href="#"', h)
    h = re.sub(r'href="https://finnian\.ca/[^"]*"', 'href="#"', h)
    h = re.sub(r'<link rel="canonical"[^>]*>', '', h)
    if ph:
        def mark(m):
            return m.group(1) + m.group(2) + " (placeholder link)" + m.group(3) if (ph == "ALL" or m.group(2).strip() in ph) else m.group(0)
        h = re.sub(r'(<a class="btn[^"]*" href="[^"]*">)([^<]+)(</a>)', mark, h)
    h = h.replace("<head>", '<head><meta name="robots" content="noindex,nofollow">', 1)
    bar = (f'<div class="vbar" style="position:sticky;top:0;z-index:99;background:#e0a800;color:#17171a;font:700 12px/1.4 monospace;padding:5px 10px;text-align:center">PREVIEW, not live. {html.escape(label)}</div>'
           '<a class="vbar" href="/v-fanuzpbo/" style="position:fixed;top:34px;left:8px;z-index:100;background:#17171a;color:#fff;font:700 13px/1 monospace;padding:9px 13px;border-radius:999px;text-decoration:none;border:1px solid #fff">&larr; Back</a>'
           '<script>if(top!==self){document.querySelectorAll(".vbar").forEach(function(x){x.remove()})}else{addEventListener("keydown",function(k){if(k.key==="Escape")location.href="/v-fanuzpbo/"})}</script>')
    return re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + bar, h, count=1)
if os.path.exists(P): shutil.rmtree(P)
os.makedirs(P + "/assets")
for st in cfg["stages"].values():   # copy release-branch-only assets
    for n in git("ls-tree", "-r", "--name-only", st["ref"], "assets").stdout.split():
        if n not in main_assets and not n.startswith("assets/email") and not n.endswith((".mp3", ".js", ".webm", ".mp4")):
            open(P + "/assets/" + os.path.basename(n), "wb").write(git("show", f"{st['ref']}:{n}", raw=True).stdout)
n_out = 0
for pg in cfg["pages"]:
    for s in dict.fromkeys([pg["thumb"]] + [c for c in pg["compare"]]):
        if s=="now" and pg.get("nowRedirect"): continue
        st = cfg["stages"][s]; h = show(st["ref"], pg["file"])
        if h is None: print("missing", pg["id"], s); continue
        os.makedirs(f"{P}/{s}", exist_ok=True)
        open(f"{P}/{s}/{pg['id']}.html", "w").write(wrap(h, st["label"], pg.get("placeholders", {}).get(s)))
        n_out += 1
print("wrote", n_out, "previews")
