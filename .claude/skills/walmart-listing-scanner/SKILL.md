---
name: "walmart-listing-scanner"
description: "Update and optimise Dunhill Walmart Marketplace listings through the Walmart connector (no browser): reads Listing Quality issues, compares against the Amazon twin (source of truth), writes Walmart-optimised title, site description, key features, attributes and images, and pushes them as an MP_MAINTENANCE feed. Use for 'Walmart scanner', 'update this Walmart listing', 'optimise Walmart SKU', 'fix Walmart listing quality', or any Walmart content, attribute or image change, single SKU or batch."
---

# Walmart Listing Scanner (connector edition)

Updates one Walmart item at a time (or a batch, one SKU per feed item) so it matches Amazon, Walmart's content rules and the Listing Quality checklist. Everything runs through the `walmart` MCP connector. No Seller Center browser session is needed.

## Hard rules
- **Amazon is the source of truth.** Every changed value needs provenance: old value, new value, source (Amazon attribute, Amazon copy, or label). Never invent or infer claims. Dietary claims, allergens and ingredients need extra rigour.
- **Never change the Walmart price.** Never call `walmart_update_price` and never put `price` in a feed, even when Listing Quality flags price competitiveness. Just report the gap.
- **Prop 65 on every item.** All Walmart listings carry the California Prop 65 warning. If `isProp65WarningRequired` is missing or "No", set it to "Yes" and add `prop65WarningText` (ask Judy for the approved wording the first time if none exists on other items).
- **Our brands only.** Copy edits only for our own brands (Gourmanity, 4YoreElves, SOV sub-brands, Magic Seasoning Blends etc.). Third-party/distributor SKUs (Brach's, Barry's, COMBOS, Monini, PFG items) are skipped: Walmart returns "Only registered brand owners can update this content". Brand name changes always need Walmart support.
- **Confirm before any live write.** Show Judy the before/after table and the exact feed JSON, and get a yes before `walmart_submit_feed`. Factual attribute fixes backed by Amazon can be bundled in. Anything compliance-related (FSMA 204, Prop 65 text, allergens) needs her explicit OK.
- **One pending feed per SKU.** Before submitting, check `walmart_feed_status` (no feedId) for a recent MP_MAINTENANCE feed for that SKU still in RECEIVED / INPROGRESS, or with `itemsProcessing > 0`. If there is one, wait. Do not stack edits.
- **Send only what changes.** MP_MAINTENANCE is a partial update: include only the attributes being changed. Do not add `processMode` (Walmart rejects it).

## Connector tools
| Tool | Use |
|---|---|
| `walmart_list_items` | Page through the catalogue (`limit` up to 200, `nextCursor`). Gives sku, productName, productType, gtin, publishedStatus, unpublishedReasons. |
| `walmart_get_item` | One SKU: productType, GTIN/UPC, itemId, price, status. |
| `walmart_listing_quality` | With `sku`: scores, every content attribute's **current value** and its issues. Without: seller-level scores. This replaces reading the Seller Center edit form. |
| `walmart_api_request` | `POST /v3/items/spec` to fetch the current spec (version, attribute names, enums) for a product type. Other read endpoints as needed. |
| `walmart_submit_feed` | Intended write path for the MP_MAINTENANCE feed (see `references/feed-template.md`). **Currently broken, see below.** |
| `walmart_feed_status` | Check processing and per-item errors. |
| `walmart_search_catalog` | Find competitor listings or confirm a GTIN match. |

**Do not use `walmart_edit_item` for live writes.** It hard-codes spec version `5.0.20240517-04_08_27` and puts `productName` under `Orderable`. Walmart rejects that version (`ERR_INT_SYS_0801003`, "ensure the feed version is supported"); every API feed sent that way in Nov 2026 failed. Its `dryRun` is still handy to get the skeleton. Re-check this if the connector is updated.

**Status 17 Nov 2026: fix found, pending confirmation.** The header `version` must carry the `-api` suffix (`5.0.20260829-12_49_39-api`); the first test with it passed ingestion (feed 18E8EB0709D852B8B8B169A606F96D5E@AX8BBgA). Earlier, a 5.0.20260829 feed without the suffix sent with `walmart_submit_feed` (with and without `subset`) was rejected at ingestion with `ERR_INT_SYS_0801003`, field `WM_SPEC_MODE` (feeds 18E8EA7CCBFC502AAC977D756C4216BA@AX8BBwA, 18E8EA8E6D095BFEAB5C1E0480FA6F3F@AX8BBgA). `WM_SPEC_MODE` is not a feed field, so the connector most likely needs to send it as a request header/parameter for the 5.0 spec. Rejected feeds never touch the item. Until the connector is fixed: do steps 1 to 6 through the connector, then apply the approved values in Seller Center (Catalog > Edit item), and confirm via `walmart_feed_status` that the SELLER_CENTER feed reaches PROCESSED / SUCCESS. Don't retry blind header variations on the live account. A connector patch (correct default version, `mart` + `processMode: MERGE` header, content fields under Visible) makes `walmart_edit_item` usable again once deployed.

## Step 1: Pick the item and read Listing Quality
1. `walmart_get_item(sku)` for productType, GTIN, itemId, publishedStatus. Skip non-Dunhill brands.
2. `walmart_listing_quality(sku)`. Record:
   - score and category values (content & discoverability, published and in stock, price competitiveness, shipping, ratings)
   - every content attribute with `issueCount > 0` and its issue title/text (e.g. `MISSING_KEY_ATTRIBUTES`, `TOO_SHORT`, `WRITTEN_POORLY`, `CONTAINS_SPELLING_ERRORS`, `NOT_VALID`)
   - the current values of `product_name`, `product_short_description`, `product_long_description` (key features as HTML `<li>`), images count, and category attributes
   - the price block: `competitorPrice` / `asin` if Walmart matched an Amazon offer
3. If `publishedStatus` is `UNPUBLISHED` or `SYSTEM_PROBLEM`, report the `unpublishedReasons` first. A wrong product type (e.g. `default`) usually causes prohibited-product unpublishing. Changing product type is a bigger edit: flag it to Judy, don't fix it silently.

## Step 2: Get the current spec for the product type
`walmart_api_request` POST `/v3/items/spec` with body
`{"feedType":"MP_MAINTENANCE","version":"5.0.20260829-12_49_39","productTypes":["<productType>"]}`.
The output is large: it is saved to a file. Parse it with a script (see `scripts/spec_summary.py`) to get:
- the allowed header `version` (enum). If Walmart has moved on, use the new value.
- the exact attribute keys under `Visible.<productType>` (camelCase and snake_case are mixed, e.g. `shortDescription`, `keyFeatures`, `food_condition`, `foodForm`, `container_material`)
- closed-list enums (Food Condition, Food Form, Spice Level, Allergen-Free Statements, Dietary Need, Container Type)

Listing Quality uses different names (`product_short_description`, `food_form`, `spice_level`). Always map to the spec key before writing the feed. Some LQ attributes (e.g. `fsma_section_204_traceability`) may not exist in the API spec for that product type. If so, they can only be set in Seller Center; list them for Judy.

## Step 3: Pull the Amazon source of truth
- ASIN: Walmart LQ `asin` field if present, else `amazon_search_listings_by_asin` / the Amazon SKU (often the Walmart SKU), else Helium 10 `list_my_products` (needs Helium 10 connector signed in).
- Copy and images: `amazon_get_listings_item` (our seller listing: title, bullets, description, images).
- Attributes: `amazon_get_catalog_item` (item_form, temperature_rating, size, unit_count, number_of_items, specialty, diet_type, allergen info, ingredients, Prop 65).

## Step 4: Write Walmart-optimised copy
- **Title (`productName`)**: Brand + key descriptors + product + food form + key claim + size + pack. 50 to 90 characters (Walmart penalises over 90, hard max 100). Use exact Amazon sizes (5.64 oz, not 5.6oz). No promo words. Address the LQ `MISSING_KEY_ATTRIBUTES` hint (e.g. add container type "Glass Bottle") only with facts from Amazon.
  - Example: `Gourmanity Sweet and Hot Smoked Spanish Paprika Powder, Kosher, 5.64 oz, 2-Pack`
- **Site description (`shortDescription`)**: a rewrite of the Amazon description in paragraph form. Follow the LQ issue text literally: `TOO_SHORT` means at least the stated word count (currently 60+; aim 150 to 200); `WRITTEN_POORLY` "too simplistic" means longer words and sentences, "too complex" means shorter ones. Repeat the product name once for SEO. Brand names flagged as spelling errors (e.g. "gourmanity") are fine to leave. Run `scripts/copy_check.py` for word count, average sentence length and em dashes.
- **Key features (`keyFeatures`, array of strings)**: change only if LQ flags them or they contradict Amazon. Plain text, one benefit per item, 3 to 10 items.
- No em dashes. Claims (Kosher, Gluten Free, Organic, Non-GMO) only if Amazon or the label states them.
- Brand voice: Gourmanity premium and globally sourced (never framed as just European), 4YoreElves whimsical, SOV elevated, Magic Seasoning Blends Cajun-Creole heritage.

## Step 5: Attributes Walmart flags
- Food Condition: from Amazon temperature_rating (Ambient → `Shelf-Stable`).
- Food Form: from Amazon item_form, mapped to the spec enum (Powder → `Powders`, Liquid → `Liquids`).
- Spice Level: `No Spice` for non-spicy items only when obviously true (syrups, sweets); otherwise from the Amazon/label heat claim.
- Container Material / Type: from Amazon; ask Judy if Amazon is silent.
- FSMA 204: only with Judy's OK. Dried spices and shelf-stable syrups are generally "Not in Scope (Food is not on FTL)". If the key isn't in the spec, it's a Seller Center job.
- Array-typed attributes (e.g. `food_condition`, `foodForm`, `container_material`, `keyFeatures`, `productSecondaryImageURL`) must be sent as JSON arrays.

## Step 6: Images
- Compare Walmart's image count/issues from LQ (`images` attribute) with Amazon's current set.
- Find high-res originals in Dropbox (`Dropbox search`): `/Dunhill Files/PL Brands/Gourmanity/Gourmanity Products/<Product>/Design/Product Photography` (studio on white), `.../Design/EBC` (lifestyle/A+), `/Bella/Gourmanity/<Category>/<Product> - <ASIN>`.
- Walmart fetches feed image URLs asynchronously, so a single-use 15-minute Dropbox `download_link` can expire before Walmart pulls it. Use a persistent public link: `create_shared_link` and change `dl=0` to `raw=1`. Or use Amazon's image URL (`https://m.media-amazon.com/images/I/<id>.jpg`).
- `mainImageUrl` must be the product alone on white. `productSecondaryImageURL` **replaces the full secondary set**, so send every image you want kept, in order. Min 1500 x 1500 px for zoom; 2200 x 2200 recommended.

## Step 7: Build, confirm, submit, verify
1. Build the feed from `references/feed-template.md` (header: `businessUnit`, `locale`, `version` with the `-api` suffix; `Orderable` with only `sku` + `productIdentifiers`, `Visible.<productType>` with the changed keys). Validate it against the spec with `scripts/spec_summary.py --validate`.
2. Show Judy a before/after table (attribute, old, new, source) plus the feed JSON. Wait for yes.
3. `walmart_submit_feed(feedType="MP_MAINTENANCE", feed=...)`. Keep the feedId.
4. `walmart_feed_status(feedId)` until `PROCESSED`. If `ERROR` with an ingestion error, read the description, fix, and resubmit (that feed never reached the item). If `itemsFailed > 0`, read `itemDetails.itemIngestionStatus[].ingestionErrors` and fix only those fields.
5. Content can take a few hours (up to 24h) to show on walmart.com. Re-run `walmart_listing_quality(sku)` after about 48h. Use `send_later` for the check-in rather than polling.
6. First live run after any connector or spec change: test on one Gourmanity SKU and confirm PROCESSED with `itemsSucceeded: 1` before batching.

## Reporting back to Judy
Short. Cover: old vs new title; attributes set (with source); images done or pending; feedId and status; what still limits the score (usually price gap or reviews, which we don't touch); anything blocked by brand ownership, missing spec keys (Seller Center only) or unpublished status.

## Batch mode
1. `walmart_list_items` (ACTIVE, page through with `nextCursor`), keep our brands only.
2. `walmart_listing_quality` per SKU; sort by lowest score, Customer Favorites first, then those with content issues.
3. Draft per SKU as above, and keep a running log (SKU, attribute, old, new, source, feedId, status) as an Excel workbook with P1/P2/P3 colour rows and autofilters.
4. After Judy approves the batch, items with the same productType can go in one feed (one `MPItem` entry per SKU). Still never two pending feeds for the same SKU.
