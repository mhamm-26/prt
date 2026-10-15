# Validation — October 15, 2026

## Passed in the cloud workspace

- `python tools/build.py`: 15 crawlable pages plus custom 404 and 410 documents.
- `python tools/check.py` against `tools/serve.py`: all 17 HTML documents,
  9 complete article bodies, 15 internal page destinations, 46 explicit URL
  mappings (also with query strings), local image existence and dimensions,
  one H1 per page, unique titles/descriptions, canonicals, sharing metadata,
  JSON-LD, sitemap, and absence of store/runtime Shopify dependencies.
- Exact article-set comparison with the original article sitemap: 9 of 9,
  including all articles found through both category listings and pagination.
- Browser checks: all 17 pages at widths 320, 390, 768, and 1440 pixels, no
  horizontal overflow, all images decoded, no JavaScript page errors.
- Mobile menu: keyboard activation, expanded state, visible Close control,
  Tab navigation, Escape and focus return, closing on link selection, and
  ordinary navigation with JavaScript disabled.
- axe-core WCAG 2 A/AA and 2.1 AA checks on all 17 pages at 390px: no violations.
  Three inherited malformed nested lists were corrected without changing text.
  Automated accessibility checks supplement, rather than replace, manual review.
- Desktop and mobile homepages and an article page were visually reviewed.
- Six retained external link variants returned HTTP 200, including Rice Lake.
  See `external-links.json`. This verifies retrieval, not all third-party
  application behavior or login-restricted content.

## Source limitations

One source Fitbit image is unavailable (404). Closed Smartabase help references
were replaced with a current known reference or marked unavailable. Historical
health claims and technical examples are preserved with notices, not certified
as current advice. See `MIGRATION.md` and `content-edits.json` for exact details.
No live hardware, Teamworks AMS account, mailbox delivery, or manufacturer service
outcome was tested.

## Deployment checks still required

GitHub push is source publication only. Production hosting, nginx syntax and
behavior on the chosen server, HTTPS, apex/www routing, DNS, mail records, live
search indexing, and the owner’s Shopify cancellation are separate cutover steps.
The checked local server uses the same URL table as the generated nginx config;
run `nginx -t` and verify the deployed HTTP responses before switching DNS.
