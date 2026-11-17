# MP_MAINTENANCE feed template (spec 5.0.20260829-12_49_39)

Checked against `POST /v3/items/spec` on 17 Nov 2026 for product type "Flavored Syrups". Re-fetch the spec if a feed errors on version.

```json
{
  "MPItemFeedHeader": {
    "version": "5.0.20260829-12_49_39",
    "mart": "WALMART_US",
    "locale": "en",
    "processMode": "MERGE",
    "subset": "EXTERNAL"
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
- Header fields allowed by the spec: version, mart, locale, processMode (MERGE/REPLACE), subset (INTERNAL/EXTERNAL), sellingChannel, feedDate, requestId, requestBatchId, subCategory, feedType. None are marked required; `version` is an enum with one allowed value.
- The header above has not yet been confirmed with a live submit. The first live feed is the test: if it errors on a header field, read the ingestion error and adjust (e.g. drop `subset`, or add `"sellingChannel": "maintenance"`), then update this file.
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
