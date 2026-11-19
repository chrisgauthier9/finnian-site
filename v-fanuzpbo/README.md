# versions (hidden page, finnian.ca/v-fanuzpbo/)

Chris and Laleh's map of which pages exist on finnian.ca and what changes are scheduled. Hidden: `noindex`,
secret path (not in `robots.txt`, which would reveal it), not in `sitemap.xml`, not linked from any page. Pushing to `main` publishes it.

Files: `pages.json` (the only thing to edit by hand), `index.html` (grid), `compare/index.html` (now vs after),
`common.css`, `previews/` (generated copies of pages), `tools/make_previews.py`.

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
