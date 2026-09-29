# finnian.ca

Chris and Laleh both work on this site, each with their own Claude. The Finnian rules (brand, naming,
naming) are in the `finnian-hq` repo's `CLAUDE.md`; read it if it is on this Mac. The technical detail
and every known trap is in `README.md`. **Read README.md before changing anything.**

## Pushing to `main` publishes the site

GitHub Pages serves `main` to finnian.ca about a minute after a push. There is no staging server.

- **Chris and Laleh both have full permission to change and publish the site.** Neither needs the other's
  review or approval. Whoever you are working with decides, and their OK is enough to push to `main`.
- Preview locally first, show them, then commit and push to `main`. No branches or merge requests needed.
- Always `git pull --rebase` before starting and before pushing. Never force-push. Never rewrite `main`.
- If the change is something the other person would want to know about, leave them an FYI line in
  `finnian-hq/handoffs.md`. It is information, not a request for approval.

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
- After a push, load the live page and check the change is there. Don't trust the diff.
