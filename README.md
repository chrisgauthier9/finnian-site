# finnian.ca

One-page site plus a `/links` page. Static HTML and CSS, no build step. Preview with
`python3 -m http.server 8787` and open http://localhost:8787.

```
index.html        home: hero, release, mailing list, links
links/index.html  the Instagram-bio page (finnian.ca/links)
ig/, tt/          bio-link redirects that count Instagram and TikTok traffic
assets/style.css  all styling; brand tokens at the top
assets/signup.js  mailing-list form (EmailOctopus)
assets/email/     images used by the EmailOctopus emails; do not rename
CNAME             finnian.ca, for GitHub Pages
```

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

## Cloudflare caches `/assets/` for four hours

Cloudflare sits in front of GitHub Pages and caches `/assets/*` with `max-age=14400`, while HTML is
not cached at all (`cf-cache-status: DYNAMIC`). So a CSS or JS change can be live at the origin and
still invisible to visitors for hours.

**Fix, and the rule for every future change: bump the `?v=` on the asset links in `index.html` and
`links/index.html` whenever `style.css` or `signup.js` changes.** The HTML is always fresh, so a new
version string pulls the new asset immediately. Purging in the Cloudflare dashboard also works but
needs a human click.

Caught 2026-09-09: the MailerLite endpoint was live at the origin while Cloudflare kept serving the
old placeholder to visitors.

## The signup form

`assets/signup.js` posts to EmailOctopus, form "finnian.ca signup":
`https://eomail5.com/form/e8ba5ea6-bbad-11f1-9ef5-ab546f8d3526` (account on contact@finnian.ca since 2026-09-29), FormData with `field_0` for the
address and the long `hp...` honeypot sent empty. It reads the JSON reply instead of assuming
success, which matters: under MailerLite a `no-cors` fetch made the form claim success for
everything, including addresses that were rejected.

**Do not turn the form's hidden reCAPTCHA back on in EmailOctopus.** Our own markup cannot produce
a reCAPTCHA token, so enabling it rejects every submission. The honeypot is the protection.

**EmailOctopus's contact search lags several minutes behind reality**, and so does the contact
count on the Contacts page. A new signup is live immediately at its own contact URL but will not
appear in the search box yet. Do not read that as a broken form.

**Do not curl the new `?v=` URL while the deploy is still running.** Cloudflare caches whatever
the origin returns at that moment, so polling `?v=9` during a deploy pins the OLD file to the NEW
version string for four hours and the bump silently does nothing. This happened on 2026-09-11.
Check the origin instead - `https://chrisgauthier9.github.io/finnian-site/assets/style.css` - and
only request the Cloudflare URL once the origin is serving the new bytes. If a version does get
poisoned, bump again rather than waiting it out.

## Bio links: finnian.ca/ig and finnian.ca/tt

Each is a one-file folder that reports itself to Cloudflare Web Analytics and then sends the
visitor to `/links/`. The point is that Instagram and TikTok strip referrers, so without separate
entry paths their traffic is indistinguishable, and a `?utm_source=` string on the end of a bio
link is ugly enough that Chris asked for something better.

**The 150ms delay in those files is deliberate.** Cloudflare injects its analytics beacon into the
page and the beacon needs a moment to report before the redirect fires. Remove the delay and the
page stops being counted, which defeats the whole thing.

To add a source, copy the folder and change the label. Keep the paths short; they are read off a
phone screen.

**Web Analytics is already on**, set up automatically when the zone moved to Cloudflare, so there
is no snippet to install. It is currently set to **"Enable, excluding visitor data in the EU"**,
which means EU visitors are not counted at all.

## Design v2, 12 September 2026

The visual layer was rebuilt from Brand Guide V1 and the Pinterest board. Paper ground with
black and yellow bands, B&W photographs with figures cut out and filled flat yellow (hero, links
tile) or blue (the download section), hand-drawn SVG marks in a sprite at the top of `index.html`,
typewriter captions in Space Mono, a contact-sheet strip, and display type ending in a yellow full
stop that is drawn by CSS (`.display--stop::after`), not typed into the copy.

**Making a silhouette.** `rembg i photo.jpg cut.png` (installed for python3.11 at
`/opt/homebrew/bin/rembg`), then extract the alpha and fill it flat:

    magick cut.png -alpha extract -level 40%,60% mask.png
    magick plate.jpg -colorspace Gray ... -colorspace sRGB -type TrueColor PNG24:plate.png
    magick PNG24:plate.png \( -size WxH xc:'#fedc00' mask.png -compose CopyOpacity -composite \) -composite -type TrueColor out.jpg

**The `PNG24:` and `-type TrueColor` are load-bearing.** A desaturated plate is re-detected as
grayscale and the yellow layer collapses to white on write. It shipped white twice before this was
found; check a pixel on the figure with `-format "%[fx:int(255*p{x,y}.g)]"` and expect 220.

Copy did not change in v2. The release-day checklist's line numbers did and were updated.
