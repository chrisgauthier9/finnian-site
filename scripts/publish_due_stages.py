#!/usr/bin/env python3
"""Auto-publish dated hub stages (v-fanuzpbo/pages.json). Generic: any stage with "at" (ISO datetime with offset) and a "ref" branch.
Stages REPLACE, they do not stack: after the merge the whole tree outside v-fanuzpbo/ and .github/ equals the branch's (live site == hub preview).
For each stage whose time has passed and whose branch is not yet an ancestor of main: merge it into main (oldest first) and push.
Idempotent (merged branches are skipped). On a merge conflict: abort that merge, change nothing, exit 3 (the workflow raises an issue).
Usage: publish_due_stages.py [--dry-run] [--now ISO] [--wait-max-min N]
  --dry-run  report what each stage would do, merge and push nothing (merges are tried in a throwaway index via `git merge-tree`)
  --now      pretend the clock is ISO (dry-run testing)
  --wait-max-min N  if the next due stage is at most N minutes away, sleep until it (cron start-up lag compensation)"""
import argparse, datetime, json, os, subprocess, sys, time
REPO = os.environ.get("HUB_REPO") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--now"); ap.add_argument("--wait-max-min", type=int, default=0)
a = ap.parse_args()
def git(*x, check=False):
    r = subprocess.run(["git", *x], cwd=REPO, capture_output=True, text=True)
    if check and r.returncode: raise SystemExit(f"git {' '.join(x)} failed: {r.stderr.strip()}")
    return r
def now(): return datetime.datetime.fromisoformat(a.now) if a.now else datetime.datetime.now(datetime.timezone.utc)
git("fetch", "-q", "origin", "main", "+refs/heads/release*:refs/remotes/origin/release*")
if not a.dry_run:
    git("checkout", "-q", "main", check=True); git("reset", "-q", "--hard", "origin/main", check=True)
cfg = json.loads(git("show", "origin/main:v-fanuzpbo/pages.json", check=True).stdout)
def ref(b): return "origin/" + b
stages = []
for sid, st in cfg["stages"].items():
    if sid == "now" or "ref" not in st: continue
    if "at" not in st: print(f"SKIP {sid}: no \"at\" datetime"); continue
    at = datetime.datetime.fromisoformat(st["at"])
    if at.tzinfo is None: print(f"SKIP {sid}: \"at\" has no UTC offset"); continue
    stages.append((at, sid, st["ref"]))
stages.sort()
def merged(b): return git("merge-base", "--is-ancestor", ref(b), "origin/main").returncode == 0
pending = [(at, sid, b) for at, sid, b in stages if not merged(b)]
if a.wait_max_min and not a.dry_run:
    nxt = [at for at, _, _ in pending if at > now()]
    if nxt and (min(nxt) - now()).total_seconds() <= a.wait_max_min * 60:
        w = (min(nxt) - now()).total_seconds() + 2; print(f"Sleeping {int(w)} s until the next stage"); time.sleep(w)

KEEP = ("v-fanuzpbo/", ".github/")   # hub and workflows always stay main's
def replace_merge(sid, b, at):
    """Stages replace, never stack: merge the branch (-X theirs), then force the whole tree outside KEEP to the branch's."""
    r = ref(b); base = git("merge-base", "origin/main", r).stdout.strip()
    git("merge", "--no-commit", "--no-ff", "-X", "theirs", r)
    # live site == exactly what the hub previews for the stage: the whole tree outside KEEP becomes the branch's
    names = lambda t: set(f for f in git("ls-tree", "-r", "--name-only", t).stdout.splitlines() if not f.startswith(KEEP))
    mine, theirs = names("HEAD"), names(r)
    for f in sorted(mine - theirs):
        x = git("rm", "-q", "-f", "--", f)
        if x.returncode: git("merge", "--abort"); return x.stderr
    for f in sorted(theirs):
        x = git("checkout", r, "--", f)
        if x.returncode: git("merge", "--abort"); return x.stderr
    c = git("commit", "-q", "--no-edit", "-m", f"Auto-publish stage {sid}: {b} replaces earlier stages at {at.isoformat()}")
    if c.returncode and "nothing to commit" not in c.stdout + c.stderr: git("merge", "--abort"); return c.stdout + c.stderr
    return True
fail = 0
for at, sid, b in stages:
    tag = f"{sid} ({b}, {at.isoformat()})"
    if not git("rev-parse", "-q", "--verify", ref(b)).stdout.strip(): print(f"ERROR {tag}: branch missing on origin"); fail = 1; continue
    if merged(b): print(f"DONE   {tag}: already on main"); continue
    if at > now(): print(f"WAIT   {tag}: due in {at - now()}"); continue
    head = "origin/main" if a.dry_run else "HEAD"
    if a.dry_run:
        r = git("merge-tree", "--write-tree", "--no-messages", head, ref(b))
        print(f"WOULD MERGE {tag}: " + ("clean" if r.returncode == 0 else "CONFLICT\n" + r.stdout.strip()))
        if r.returncode: fail = 3
        continue
    m = replace_merge(sid, b, at)
    if m is not True:
        print(f"CONFLICT {tag}: aborted, nothing pushed\n{m}"); fail = 3; continue
    for i in range(5):
        if git("push", "origin", "main").returncode == 0: print(f"MERGED {tag} and pushed"); break
        git("fetch", "-q", "origin", "main"); git("rebase", "-q", "origin/main")
    else: print(f"ERROR {tag}: push failed"); fail = 1
sys.exit(fail)
