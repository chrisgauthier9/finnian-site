# finnian.ca

Chris and Laleh both work on this site, each with their own Claude. The Finnian rules (brand, naming,
approvals) are in the `finnian-hq` repo's `CLAUDE.md`; read it if it is on this Mac. The technical detail
and every known trap is in `README.md`. **Read README.md before changing anything.**

## Pushing to `main` publishes the site

GitHub Pages serves `main` to finnian.ca about a minute after a push. There is no staging server.

- **Laleh's changes go on a branch**, named `laleh/<what-it-is>`, e.g. `laleh/new-hero`. Commit and push
  the branch, then leave Chris a note in `finnian-hq/handoffs.md` saying what changed and which branch.
  **Chris's Claude reviews it and merges it to `main`. That merge is the publish.**
- **Chris's own changes** go to `main` after he approves the wording, as before.
- Always `git pull --rebase` before starting, and before merging.
- Never force-push. Never rewrite `main`.

## Previewing

Run `python3 -m http.server 8787` in this folder and open http://localhost:8787. Check the phone width as
well as desktop. That preview is the only one; nothing on a branch is visible online.

## Rules that bite

- **Changed `style.css` or `signup.js`? Bump the `?v=` number** on its link in `index.html` and
  `links/index.html`. Otherwise Cloudflare serves the old file for four hours.
- **Keep `sitemap.xml` in sync** with the pages that exist.
- **Never assume who is in a photo** before putting it on the site. Ask.
- **Links to the release always point at the Hypeddit link**, `hypeddit.com/finnian/<slug>`.
- **Don't touch `assets/email/`** without saying so in a handoff. The live emails load those images.
- After a merge, load the live page and check the change is there. Don't trust the diff.
