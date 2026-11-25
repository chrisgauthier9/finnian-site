#!/usr/bin/env python3
"""Check that the version hub (v-fanuzpbo/pages.json) matches the real release branches.
Run from anywhere: python3 scripts/check_hub.py   (exit 1 when something is off)
- every release/* and release-* branch must be a stage ref, or be listed under "retired" in pages.json
- every html page a stage branch changes vs main must be a page whose `changes` and `compare` include that stage
- every page's `changes` stage must really have that file on the stage's branch
- every page `file` must exist on main, or have a stage
- pages not on main, or download pages with a pending stage, must carry "release": "YYYY-MM-DD"
- warns when a stage branch is far behind main (merging it could undo live edits)
A stage may carry "ignore": [files] for known-stale leftovers."""
import os, json, subprocess, sys
V = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "v-fanuzpbo")
REPO = os.path.dirname(V)
cfg = json.load(open(V + "/pages.json"))
def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True); return r.stdout.strip() if r.returncode == 0 else None
def ref(b):
    for c in (b, "origin/" + b):
        if git("rev-parse", "--verify", "-q", c): return c
subprocess.run(["git", "fetch", "-q", "origin"], cwd=REPO, capture_output=True)
problems, notes = [], []
stages = {k: v for k, v in cfg["stages"].items() if k != "now"}
branches = set()
for line in (git("branch", "-a", "--format=%(refname:short)") or "").splitlines():
    b = line.replace("origin/", "", 1)
    if b.startswith(("release/", "release-")) and b != "release-day": branches.add(b)
refs = {s["ref"] for s in stages.values()}
retired = set(cfg.get("retired", []))
for b in sorted(branches - refs - retired):
    problems.append(f"branch {b} is not a hub stage and not in 'retired': add it as a stage or retire it")
byfile = {p["file"]: p for p in cfg["pages"]}
for sid, st in stages.items():
    r = ref(st["ref"])
    if not r: problems.append(f"stage {sid}: ref {st['ref']} does not exist"); continue
    changed = [f for f in (git("diff", "--name-only", f"main...{r}") or "").splitlines()
               if f.endswith(".html") and not f.startswith("v-fanuzpbo/") and f not in st.get("ignore", [])]
    for f in changed:
        p = byfile.get(f)
        if not p: problems.append(f"stage {sid} ({st['ref']}) changes {f}: not in pages.json")
        elif sid not in p["changes"] or sid not in p["compare"]: problems.append(f"stage {sid} changes {f}: page '{p['id']}' lacks '{sid}' in changes/compare")
    behind = int(git("rev-list", "--count", f"{r}..main") or 0)
    if behind > 20: notes.append(f"stage {sid} ({st['ref']}) is {behind} commits behind main: rebase before its day or it may undo live edits")
for p in cfg["pages"]:
    for sid in p["changes"]:
        st = cfg["stages"].get(sid)
        r = ref(st["ref"]) if st else None
        if not r: problems.append(f"page {p['id']}: stage {sid} unknown"); continue
        if git("rev-parse", "-q", "--verify", f"{r}:{p['file']}") is None: problems.append(f"page {p['id']}: {p['file']} missing on {st['ref']}")
        elif sid not in p["compare"]: problems.append(f"page {p['id']}: '{sid}' in changes but not compare")
    if git("rev-parse", "-q", "--verify", f"main:{p['file']}") is None and not p["changes"]:
        problems.append(f"page {p['id']}: {p['file']} is not on main and has no stage")
import datetime
for p in cfg["pages"]:
    not_on_main = git("rev-parse", "-q", "--verify", f"main:{p['file']}") is None
    if not p.get("release") and (not_on_main or (p.get("type") == "download" and p["changes"])):
        problems.append(f"page {p['id']}: unreleased track page (not on main, or download with a pending stage) lacks \"release\": \"YYYY-MM-DD\" in pages.json")
    if p.get("release"):
        try: datetime.date.fromisoformat(p["release"])
        except ValueError: problems.append(f"page {p['id']}: bad release date {p['release']}")
for n in notes: print("NOTE", n)
for x in problems: print("MISMATCH", x)
print("hub matches branches" if not problems else f"{len(problems)} mismatch(es): fix v-fanuzpbo/pages.json, run tools/make_previews.py")
sys.exit(1 if problems else 0)
