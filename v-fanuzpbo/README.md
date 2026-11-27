# versions (hidden page, finnian.ca/v-fanuzpbo/)

Chris and Laleh's map of which pages exist on finnian.ca and what changes are scheduled. Hidden: `noindex`,
secret path (not in `robots.txt`, which would reveal it), not in `sitemap.xml`, not linked from any page. Pushing to `main` publishes it.

Files: `pages.json` (the only thing to edit by hand; `scripts/check_hub.py` at the repo root verifies it), `index.html` (grid), `compare/index.html` (now vs after),
`common.css`, `previews/` (generated copies of pages), `tools/make_previews.py`.

## Rule: the hub moves with the branch (2026-11-25)
**Any chat that creates or changes a site release branch (`release/*`, `release-*`) or adds/removes a page must update `pages.json` in the same push**: the branch under `stages` (label with the go-live time, Eastern), every changed page in `pages`, `changes` and `compare`, a new page's entry, and `retired` for a branch that has gone live or been dropped. Then run `python3 v-fanuzpbo/tools/make_previews.py` and `python3 scripts/check_hub.py` (lists branches and changed pages missing from `pages.json`, exits 1 on a mismatch) and push `main`. A release is not done until the check passes. When the stage goes live, follow "When a change goes live" below.

**Dated stages auto-publish (2026-11-26).** Every stage in `pages.json` carries `"at": "YYYY-MM-DDTHH:MM:SS-05:00"` (ISO with Toronto offset; `check_hub.py` requires it). `.github/workflows/publish-due-stages.yml` runs every 15 min (a run starting within 25 min of a stage sleeps until it), and `scripts/publish_due_stages.py` merges each stage whose time has passed and whose branch is not on main into `main` (oldest first) and pushes, then requests a Pages build. Idempotent (merged branches are skipped). On a conflict nothing is forced: the run fails and opens a GitHub issue "Stage auto-publish failed". Any stage name works, so a new stage flips with no new code. Dry-run: `python3 scripts/publish_due_stages.py --dry-run [--now 2026-12-01T00:01:00-05:00]` (each stage tested alone against main; for a real sequence test merge them in order in a scratch worktree). After a stage goes live, still do "When a change goes live" below. **A gate WAV/file swap is not part of this**; it stays a separate box job per release (`~/gate-release/` on the box).

**Every page for an unreleased track carries `"release": "YYYY-MM-DD"` in `pages.json`** (the go-live date, Eastern). The hub card and editor header show a red "Unreleased, out Dec 1" badge until that date, then it vanishes by itself; `check_hub.py` fails if a download page with a stage, or a page not yet on main, lacks it. Remove the field (or leave it) once live.

## Add a page
1. Add an entry to `pages` in `pages.json`: `id` (short, unique), `type` (`main`, `release` or `download`: which section it sits in; pages with changes list first), `name`, `url`, `file` (path in the site repo), `thumb` (`now`),
   `changes` (`[]`), `compare` (`[]`).
2. Run `python3 v-fanuzpbo/tools/make_previews.py`, then commit `v-fanuzpbo/` and push.

## Add an upcoming change
1. Put the edited page on a release branch (never merged until its day), add the branch under `stages` in `pages.json`
   (`"dec18": {"label": "Dec 18", "ref": "release/..."}`) if the stage is new.
2. On the page's entry: add the stage id to `changes` (drives the orange "Changes Dec 18" badge) and to `compare`
   (order: `now` first, then each stage). `thumb` is the stage shown on the card. For a brand-new page use its first stage as `thumb`.
   Optional: `placeholders` (`{"dec18": "ALL"}` or a list of button labels) marks fake store links "(placeholder link)";
   `nowRedirect` (text) shows a "redirect, no page" tile when the live page only redirects.
3. **The previews must be copied in**: run `python3 v-fanuzpbo/tools/make_previews.py` (reads each stage's git ref, writes
   `v-fanuzpbo/previews/<stage>/<id>.html`, strips tracking and redirect scripts, adds the PREVIEW banner and Back button).
   Re-run it whenever a release branch changes, then commit `v-fanuzpbo/` and push. Needs the release branches fetched locally.

## When a change goes live
Merge the release branch as usual, then in `pages.json` drop that stage from `changes` and `compare` (and the stage if unused),
set `thumb` to `now`, re-run `make_previews.py`, push.

Each card and hidden redirect also shows "Open live", linking to `https://finnian.ca` + the entry's `url` (derived, no extra field; new pages not yet merged will 404 there until release).

Never link `/v-fanuzpbo/` from the site. Keep it out of `sitemap.xml`.

Changed `common.css`? Bump the `?v=` on its link in `index.html` and `compare/index.html` (Cloudflare caches it 4 hours). Same for `pages.json` if edits do not show: open it once with `?x=1` to confirm.

Previews are silent on purpose: `make_previews.py` strips all scripts, audio/video/iframes and autoplay from the copies, and the thumbnails are sandboxed iframes. Do not add players back.

## Tap-to-edit (v1.0, 2026-11-20)
Open the hub, press **Edit: off** (top, shown only on a signed-in device) so it reads **Edit: on**, tap a page, then tap any text, button or link on the rendered page. A bottom sheet edits it (link text and its address together). **Publish now** commits to `main`; **Schedule** takes a Toronto date and time (the 5-minute cron commits it). On a staged version tab (Nov 20, Dec 1, ...) the button reads **Save to <date>** and commits to that release branch instead.
- `edit/index.html` is the page; it calls the finnian-gate Worker (`/admin/api/render|publish|schedule|scheduled|cancel`, source `gate/src/admin.js`) with the secret in the `X-Admin-Token` header (CORS only for finnian.ca). The public hub holds no secret and cannot write.
- Sign in once per device by opening the private hub link (`/admin/hub/<secret>`, kept in `Projects/Finnian/portal-link.txt` and Keychain, never committed). It redirects here with the token in the URL fragment; the hub stores it in localStorage and clears the URL.
- The Worker renders the real source with every text node and link tagged with its parse id; an edit sends id, original text and the file's blob sha. It refuses if the text or the sha no longer matches (a changed page, a wrong node), so no regex or guessing.
- Not editable: structure, images, new pages, `<title>`, option labels. `previews/` thumbnails are not refreshed by an edit; re-run `make_previews.py`.
