# MP_MAINTENANCE feed template (spec 5.0.20260829-12_49_39)

Checked against `POST /v3/items/spec` on 17 Nov 2026 for product type "Flavored Syrups". Re-fetch the spec if a feed errors on version.

```json
{
  "MPItemFeedHeader": {
    "businessUnit": "WALMART_US",
    "locale": "en",
    "version": "5.0.20260829-12_49_39-api"
  },
  "MPItem": [
    {
      "Orderable": {
        "sku": "<SKU>",
        "productIdentifiers": { "productIdType": "GTIN", "productId": "<14-digit GTIN from walmart_get_item>" }
      },
      "Visible": {
        "<productType exactly as walmart_get_item returns it>": {
          "productName": "<new title>",
          "shortDescription": "<site description>",
          "keyFeatures": ["<feature 1>", "<feature 2>"],
          "food_condition": ["Shelf-Stable"],
          "foodForm": ["Liquids"],
          "spiceLevel": "No Spice",
          "container_material": ["Glass"],
          "isProp65WarningRequired": "Yes",
          "prop65WarningText": "<approved wording>",
          "mainImageUrl": "<url>",
          "productSecondaryImageURL": ["<url>", "<url>"]
        }
      }
    }
  ]
}
```

Notes
- Include only the keys you are changing. Remove the rest.
- `Orderable` requires `sku` and `productIdentifiers`. Never add `price`.
- In this spec version `productName`, `brand` and `mainImageUrl` live under `Visible`, not `Orderable`.
- **Confirmed header (17 Nov 2026 live tests): `businessUnit`, `locale`, `version` with the `-api` suffix. Nothing else.** The Get Spec response lists mart/processMode/subset etc., but Walmart's ingestion rejects `processMode` ("not a valid field") and requires `businessUnit`. Trust ingestion errors over the spec file for the header.
- Partial update is the default for MP_MAINTENANCE: only the attributes you send change.
- 17 Nov 2026: without the `-api` suffix, feeds are rejected instantly with ERR_INT_SYS_0801003 on field WM_SPEC_MODE.
- **API feeds need the `-api` suffix on the version** (`5.0.20260829-12_49_39-api`). Without it Walmart rejects the feed instantly on WM_SPEC_MODE. With it, the 17 Nov test feed 18E8EB0709D852B8B8B169A606F96D5E@AX8BBgA passed ingestion (outcome: see SKILL.md status note). Seller Center feeds show the version without the suffix.
- When fetching the spec, `/v3/items/spec` accepted the version without the suffix.
- Seller Center feeds that succeeded in Nov 2026 used version `5.0.20260829-12_49_39`. API feeds on `5.0.20240517-04_08_27` failed with `ERR_INT_SYS_0801003`.

Listing Quality name → spec key (examples)
| Listing Quality | Spec key |
|---|---|
| product_name | productName |
| product_short_description | shortDescription |
| product_long_description | keyFeatures (array) |
| food_form | foodForm |
| food_condition | food_condition |
| spice_level | spiceLevel |
| container_type | containerType |
| container_material | container_material |
| count_per_pack | countPerPack |
| multipack_quantity | multipackQuantity |
| number_of_pieces | pieceCount |
| ingredient_list_image | ingredientListImage |
| nutrition_facts_label | nutritionFactsLabel |
| images | mainImageUrl + productSecondaryImageURL |
| fsma_section_204_traceability | not in the API spec for some types: Seller Center only |
