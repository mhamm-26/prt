# Pro Recovery Tech resource center

A lightweight, static replacement for the former Shopify store. Nine full
educational articles retain their original `/blogs/...` URLs. The site uses the
original locally stored logo, favicon, Assistant fonts, and available article
imagery. There is no database, package-install step, store, tracking, or Shopify
runtime dependency.

## Build and preview

Requires Python 3.10 or newer. From the repository root:

```sh
python tools/build.py
python tools/serve.py --port 8000
```

Open the preview server on port 8000. In a second terminal run:

```sh
python tools/check.py
```

`dist/` is generated and ignored. It contains the entire deployable static site.
The preview server applies the same route table used to generate the nginx
configuration, including real 301, 404, and 410 responses. Do not use Python's
plain `http.server` for migration validation: it does not apply these mappings.

## Edit content

- `content/articles/*.html`: full, editable article bodies.
- `content/articles.json`: titles, original dates/authors, descriptions, images,
  table-of-contents entries, and context notices.
- `content/routes.json`: explicit URL migration decisions.
- `tools/build.py`: shared layouts and informational pages.
- `public/assets/`: local brand assets, images, fonts, CSS, and minimal menu JS.

Run the build after edits. Keep original publication dates; add a meaningful
revision date only after a substantive technical revision. The 2026 migration
notice is an editorial presentation date, not a claim of technical revalidation.
Article URLs deliberately have no trailing slash, matching the source URLs.
The nine-item library fits on one page; categories use ordinary links and work
without JavaScript.

## Publish the website

Pushing this repository to GitHub does **not** replace the live Shopify website.
See [hosting instructions](docs/HOSTING.md) and the [cutover checklist](docs/CUTOVER.md).
Upload only `dist/` as the web root. Keep backups, tools, and documentation out of
that root. Configure the supplied HTTP routing rules before changing DNS.

## Migration evidence and limitations

See [migration report](docs/MIGRATION.md), [URL mapping](docs/url-migration.csv),
[content edits](docs/content-edits.json), [asset inventory](docs/asset-inventory.json),
and [validation notes](docs/VALIDATION.md). One original Fitbit image is missing
at the source; obsolete help references are identified in the report. No brand
statistics, testimonials, or client logos were carried over without verification.

## Optional development checks

`tools/browser_check.py` uses Python Playwright, `/usr/bin/chromium`, and a local
axe-core script supplied in `AXE_SCRIPT`. These are development-only dependencies;
they are never shipped to visitors. The standard-library check is independent of
these tools.

`tools/backup_source.py` creates a raw, ignored source archive with checksums and
follows blog pagination and sitemaps. `tools/import_content.py` is a **one-time
migration tool**, requiring Beautiful Soup and Pillow, and consumes that archive.
It overwrites migrated content; do not rerun it after manual content edits unless
you have preserved those edits. Normal builds never contact the old site.
