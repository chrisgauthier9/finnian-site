# versions (hidden page, finnian.ca/versions/)

Chris and Laleh's map of which pages exist on finnian.ca and what changes are scheduled. Hidden: `noindex`,
`Disallow: /versions/` in `robots.txt`, not in `sitemap.xml`, not linked from any page. Pushing to `main` publishes it.

Files: `pages.json` (the only thing to edit by hand), `index.html` (grid), `compare/index.html` (now vs after),
`common.css`, `previews/` (generated copies of pages), `tools/make_previews.py`.

## Add a page
1. Add an entry to `pages` in `pages.json`: `id` (short, unique), `name`, `url`, `file` (path in the site repo), `thumb` (`now`),
   `changes` (`[]`), `compare` (`[]`).
2. Run `python3 versions/tools/make_previews.py`, then commit `versions/` and push.

## Add an upcoming change
1. Put the edited page on a release branch (never merged until its day), add the branch under `stages` in `pages.json`
   (`"dec18": {"label": "Dec 18", "ref": "release/..."}`) if the stage is new.
2. On the page's entry: add the stage id to `changes` (drives the orange "Changes Dec 18" badge) and to `compare`
   (order: `now` first, then each stage). `thumb` is the stage shown on the card. For a brand-new page use its first stage as `thumb`.
   Optional: `placeholders` (`{"dec18": "ALL"}` or a list of button labels) marks fake store links "(placeholder link)";
   `nowRedirect` (text) shows a "redirect, no page" tile when the live page only redirects.
3. **The previews must be copied in**: run `python3 versions/tools/make_previews.py` (reads each stage's git ref, writes
   `versions/previews/<stage>/<id>.html`, strips tracking and redirect scripts, adds the PREVIEW banner and Back button).
   Re-run it whenever a release branch changes, then commit `versions/` and push. Needs the release branches fetched locally.

## When a change goes live
Merge the release branch as usual, then in `pages.json` drop that stage from `changes` and `compare` (and the stage if unused),
set `thumb` to `now`, re-run `make_previews.py`, push.

Never link `/versions/` from the site. Keep it out of `sitemap.xml`.
