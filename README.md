# finnian.ca

One-page site plus a `/links` page, built 2026-09-08 for the **You Got Me** release on 2026-09-24.
Deadline in the release sequence: **live by Sept 19**.

Static HTML and CSS, no build step. Open `index.html` or run `python3 -m http.server 8787`.

```
index.html        hero, release, mailing list, links
links/index.html  the Instagram-bio page (finnian.ca/links)
assets/style.css  all styling; brand tokens at the top
assets/signup.js  mailing-list form; set SIGNUP_ENDPOINT
assets/hero.jpg   NOT PRESENT YET. Drop it in and it paints itself.
assets/avatar.jpg NOT PRESENT YET. Same.
CNAME             finnian.ca, for GitHub Pages
```

## What still has to be filled in

1. **`assets/hero.jpg`** and **`assets/avatar.jpg`**. Until they exist the page falls back to a dark
   gradient and a plain disc, so it is shippable without them. Laleh picks the frame.
2. **`SIGNUP_ENDPOINT`** in `assets/signup.js`. Empty means the form opens a pre-filled email to
   contact@finnian.ca instead of failing, so it is never a dead end. MailerLite is the pick: its free
   tier includes automations, which is what delivers the three remixes on signup.
3. **The pre-save link**, once DistroKid has delivered (around Sept 15). Marked `TODO` in
   `links/index.html`; on `index.html` the Pre-save button currently drops to the signup form.

The links themselves are done, lifted from `linktr.ee/finnian.music` on 2026-09-08: Instagram
`@finnian.music`, SoundCloud `@finnian_music`, TikTok `@finnian_music`, the YouTube channel, and the
three featured items (baianà, Mimosa 2000, the IF YOU FANCY radio set). **Retire the Linktree once
this is live**; owning `/links` is the whole point.

## Deploying (GitHub Pages, keeps Google Workspace mail untouched)

Cloudflare Pages would mean moving nameservers off GoDaddy and recreating the Google MX records.
GitHub Pages publishes plain A records at the apex, so DNS changes stay limited to the web records.

```bash
gh repo create chrisgauthier9/finnian-site --public --source . --push
```

Then in the repo, Settings → Pages → deploy from `main` / root, custom domain `finnian.ca`,
Enforce HTTPS on.

At GoDaddy DNS, **replace the existing A records** (they point at the Website Builder
"Launching Soon" page, currently 76.223.105.230 and 13.248.243.5):

| Type | Name | Value |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | chrisgauthier9.github.io |

**Leave the MX records alone.** They are Google Workspace and carry contact@finnian.ca.

## Analytics

Nothing is tracking yet, which is the point of hosting `/links` here rather than on Linktree.
Cloudflare Web Analytics is a free one-line beacon and needs no DNS change; add it before Sept 19.
