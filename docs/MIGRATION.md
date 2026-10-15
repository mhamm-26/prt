# Migration report — October 15, 2026

## Scope and evidence

The live site, both blog category listings, Data & AMS pagination (`?page=2`),
and the article sitemap were inspected. **All 9 sitemap articles are migrated:**
7 Data & AMS and 2 Health & Performance. All original article paths are retained.
The raw backup captured 580 URLs successfully out of 581 attempted, including
HTML, sitemaps, and source asset variants. The sole failed request is the missing
Fitbit image described below. Backups are not public website content.

Original full bodies, headings, instructions, available imagery, author names,
and displayed original dates were retained, subject to the explicit commercial
removals in `content-edits.json`. That file records removed passages and links.
`content/articles.json` records original page checksums and before/after word
counts. Unchanged guides have matching word counts; removals and inserted
availability notes explain the other differences. Images are optimized local
copies; original asset URLs and hashes are recorded in `asset-inventory.json`.

## Article inventory

| Category | Article | Original publication | Author | Original / migrated words |
| --- | --- | --- | --- | --- |
| Data & AMS | [How to set up your Rice Lake Bluetooth Scale with Teamworks AMS](https://prorecoverytech.com/blogs/news/how-to-set-up-your-rice-lake-bluetooth-scale-with-teamworks-ams) | November 16, 2025 | Milo Connelly | 242 / 215 |
| Data & AMS | [Rice Lake Bluetooth Physician Scales](https://prorecoverytech.com/blogs/news/rice-lake-bluetooth-physician-scales) | October 21, 2024 | Milo Connelly | 300 / 261 |
| Health & Performance | [Unlocking Peak Performance: The Benefits of Whole Body Red Light Therapy](https://prorecoverytech.com/blogs/health-performance/unlocking-peak-performance-the-benefits-of-whole-body-red-light-therapy) | October 14, 2024 | Milo Connelly | 542 / 542 |
| Health & Performance | [A Closer Look at the Fitbit Inspire 3: Features and Sleep Tracking Reliability](https://prorecoverytech.com/blogs/health-performance/fitbit-inspire-3-activity-sleep-tracker) | October 2, 2024 | Milo Connelly | 629 / 622 |
| Data & AMS | [3 Ways to Integrate Data into a Teamworks AMS (Smartabase) Site](https://prorecoverytech.com/blogs/news/3-ways-to-integrate-data-into-a-teamworks-ams-smartabase-site) | September 25, 2024 | Milo Connelly | 732 / 739 |
| Data & AMS | [What is an API? A Simple Guide for Integrating Data in AMS](https://prorecoverytech.com/blogs/news/what-is-an-api-a-simple-guide-for-integrating-data-in-athlete-management-systems) | September 17, 2024 | Milo Connelly | 759 / 759 |
| Data & AMS | [Installing smartabaseR - A step by step guide](https://prorecoverytech.com/blogs/news/installing-smartabaser-a-step-by-step-guide) | June 6, 2024 | Milo Connelly | 295 / 274 |
| Data & AMS | [Breaking Down the Teamworks Gatorade Weight Tracking Solution](https://prorecoverytech.com/blogs/news/breaking-down-the-teamworks-gatorade-weight-tracking-solution) | March 12, 2024 | Milo Connelly | 496 / 486 |
| Data & AMS | [Rice Lake Bluetooth Scale Integration with Smartabase](https://prorecoverytech.com/blogs/news/rice-lake-bluetooth-scale-integration-with-smartabase-emr) | March 5, 2024 | Milo Connelly | 289 / 200 |

## Source issues and editorial decisions

- **Missing image:** `IMG_8709_480x480.png?v=1727055792` in the Fitbit article
  returns 404. The full-size `IMG_8709.png` variant also returns 404. No substitute
  was invented. An inline availability note replaces that missing image.
- **Closed help center:** three `smartabase.zendesk.com` links redirect to a
  Zendesk “help center closed” page. The Bluetooth scale guide uses the current
  Teamworks help link already present in the newer source article. The API and
  Gx references are marked unavailable, with their original URLs recorded in the
  edit log. HTTP success alone was not treated as a working reference.
- **Historical code:** the smartabaseR guide's unquoted `install.packages(devtools)`
  and `df -> sb_get_event(...)` example are retained, with an explicit caution.
  No live AMS integration or credentials were tested.
- **Conflicting compatibility claims:** the earliest Rice Lake article says one
  model is compatible, while a later article describes three. The discrepancy is
  flagged; technical statements were not silently corrected.
- **Health claims:** the original studies, citations, and example red-light
  protocol were retained. They are not independently verified or represented as
  current clinical guidance. Older Fitbit citations do not directly validate
  the Inspire 3. Each health article has a prominent context notice.
- **Historical credibility:** the old homepage displays collegiate logos,
  “40+” clients, “125+” shipments, and “100% Satisfaction.” Authorization and
  substantiation could not be established, so none are presented on the new site.
- **Contact:** the public `sales@prorecoverytech.com` address was found on the
  original site. Delivery was not tested. Rice Lake inquiries are routed to the
  official Rice Lake website; no support outcomes are promised.
- **Old policies:** privacy redirects to the new actual-functionality policy.
  Refund, shipping, and terms pages return 410; they remain in the private source
  backup for historical reference rather than as active policies.
- **Retired products:** all 10 product sitemap URLs are individually mapped.
  The older Fitbit product URL found in article content is also mapped. Matching
  model guides are used where relevant; stands, accessories, firmware, and
  unmatched products are retired with 410. Unknown URLs return 404.

The new site has no purchase links, prices, account/cart/checkout functionality,
store search, Shopify scripts, Product/Offer/rating markup, or remotely loaded
Shopify assets. External links are references or explicit contact destinations.

## Backup retention

The full raw archive is in the workspace's ignored `backups/` directory. It is
85 MB and includes redundant original image variants. Copy it to durable private
storage before terminating the environment or canceling Shopify. Only clean
migrated content and selected local assets are committed to the public website
repository; raw store HTML is intentionally excluded from deployment.
