# Hosting the static website

## Vercel

The committed `vercel.json` configures the Python build, `dist` output directory,
and all page/redirect/error routes. Import this GitHub repository with:

- Framework preset: **Other**
- Root Directory: repository root (leave blank)
- Production Branch: **main**

The repository configuration supplies Build Command `python3 tools/build.py`,
Output Directory `dist`, and no install step. Remove conflicting dashboard
command overrides if you previously set them. Deploy the latest main commit;
if automatic Git deployments are disabled, manually redeploy that commit.

A Vercel platform `404 NOT_FOUND` at `/` is different from this site's custom 404:
check that the deployment built this repository root and published `dist`, and
that the domain points to that deployment. Do not publish `public` as the output:
it contains assets but no generated pages.

`python tools/build.py` regenerates `vercel.json` from the same route table as
nginx. Commit any resulting configuration changes before deployment, because
Vercel reads configuration before running the build. Run
`python tools/check_vercel.py` to validate route targets and redirect behavior.
The config preserves original article URLs, 301s, retired-page 410s, and a true
custom 404. There is no homepage catch-all.

## Alternative: an nginx static host

1. Run `python tools/build.py` in the repository root.
2. Copy the **contents** of `dist/` to `/srv/prorecoverytech/` on your host.
3. Copy `hosting/nginx-routes.conf` to `/etc/nginx/snippets/prt-routes.conf`.
4. Use `hosting/nginx-server.example.conf` as the basis for the virtual host.
   Configure HTTPS certificates and apex/www redirects using your host's normal
   tooling. The example listens on port 80 for staging; it is not an HTTPS setup.
5. Run `nginx -t` on the actual host, then reload nginx. The cloud preview tests
   do not replace this deployment-specific syntax/configuration check.
6. Confirm each row in `docs/url-migration.csv` returns its specified HTTP status.
   301 responses must have the specified Location; 410s must retain the 410 status
   while showing the helpful retired-page document. Unknown URLs return 404.
7. Check all production pages, the sitemap, and HTTPS before changing web DNS.

The route include is generated from `content/routes.json`; update that file and
rebuild rather than editing generated rules. Original article URLs resolve in
place. Old blog-listing queries such as `?page=2` redirect to the complete category
library; all seven Data & AMS articles are available on that one page.

## Other providers

Any static host can serve the files, but it must also support the migration
behavior. Translate **every** non-200 row in `docs/url-migration.csv` into that
provider's redirect/error configuration. Do not use an SPA fallback to Home:
that would create incorrect 200 responses for removed products and policies.
GitHub Pages alone does not provide the required general 301/410 routing.

Use build command `python tools/build.py` and output directory `dist` on a host
that provides Python. Alternatively upload the prebuilt `dist` directory.
There are no runtime packages, credentials, or environment variables.

## Privacy and retention

The example nginx host disables access logs and sets error logging to `warn`.
Confirm any CDN, platform logs, analytics, or injected scripts separately. Update
the privacy page if the production host adds services or storage. Verify that the
original public contact email still receives mail; no message was sent as part of
this migration.

## Before launch

Serve staging with `X-Robots-Tag: noindex` and remove that staging-only header on
the production host. Canonicals and sitemap entries already use the production
apex domain. Do not cancel Shopify until the [cutover checklist](CUTOVER.md) is
complete and the source archive is copied to owner-controlled durable storage.
