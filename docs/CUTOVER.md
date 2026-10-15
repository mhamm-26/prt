# Migration and cutover checklist

The replacement is built locally. Complete these deployment and ownership checks
before changing DNS or canceling Shopify. GitHub publication is not a live-site cutover.

## Preserve the source before canceling Shopify

- Source-site access is enabled and a raw backup was captured on October 15, 2026.
  Preserve that archive in owner-controlled storage before proceeding.
- Run `python tools/backup_source.py` from the repository root. Raw backups stay
  in ignored `backups/`; copy them to owner-controlled durable storage.
- Review the manifest for failed requests. Compare both category listings,
  pagination, and sitemap entries to an article-by-article migration inventory.
- Inspect the original pages visually. Archive original logos, favicon, article
  imagery, captions, author names, dates, and complete article HTML. The backup
  helper does not discover CSS background images or JavaScript-injected media;
  inspect those separately. Do not consider a crawl alone proof of completeness.
- Export store records needed for business retention separately and securely.
  Do not publish customer data or raw Shopify page backups.
- Record every product and policy URL. Decide individually between a genuinely
  relevant replacement and a 404/410; do not redirect all retired URLs to Home.

## Prepare hosting

- Choose static hosting with configurable HTTP 301 redirects and 404/410 status
  responses. GitHub source hosting alone does not publish a website.
- Test on a staging hostname before changing DNS. Ensure staging is excluded
  from indexing and production canonicals use `https://prorecoverytech.com`.
- Verify every article, local asset, menu, keyboard interaction, small-screen
  layout, metadata entry, sitemap URL, and redirect/status response.
- Confirm no runtime Shopify assets, API calls, checkout links, trackers, or
  active store policies remain. Confirm privacy text matches actual hosting logs
  and any services deliberately enabled at launch.

## Domain and launch

- Confirm owner access to the domain registrar and DNS before cancellation.
  If Shopify manages the domain, arrange independent management first.
- Export the current DNS zone. Preserve MX, SPF, DKIM, DMARC, and verification
  records; change only the records required for web hosting.
- Provision HTTPS for apex and www. Choose one canonical host and redirect the
  other. Configure the final explicit URL migration table at the host.
- Reduce DNS TTL ahead of the cutover if appropriate; record rollback values.
- Test the replacement against the production host configuration before launch.
- Change web DNS, verify HTTPS and redirects externally, submit the sitemap,
  and monitor crawl errors and broken links.
- Cancel Shopify only after the content backup, domain/email continuity, and
  replacement have all been verified. Retain backups and the migration table.
