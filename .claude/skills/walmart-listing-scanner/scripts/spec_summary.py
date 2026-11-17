#!/usr/bin/env python3
"""Summarise a Walmart /v3/items/spec response and optionally validate a feed.

Usage:
  python3 spec_summary.py SPEC_FILE                      # header version + attribute keys + enums
  python3 spec_summary.py SPEC_FILE --attr foodForm      # full detail for one attribute
  python3 spec_summary.py SPEC_FILE --validate FEED.json # check a feed against the spec
"""
import json
import sys


def load_spec(path):
    text = open(path, encoding="utf-8").read()
    data = json.loads(text[text.index("{"):])
    return data.get("schema", data)


def visible_types(spec):
    return spec["properties"]["MPItem"]["items"]["properties"]["Visible"]["properties"]


def enum_of(prop):
    if "enum" in prop:
        return prop["enum"]
    items = prop.get("items", {})
    return items.get("enum")


def summary(spec):
    hdr = spec["properties"]["MPItemFeedHeader"]["properties"]
    print("Header version enum:", hdr["version"].get("enum"))
    orderable = spec["properties"]["MPItem"]["items"]["properties"]["Orderable"]
    print("Orderable required:", orderable.get("required"))
    for ptype, body in visible_types(spec).items():
        print(f"\nVisible.{ptype} ({len(body['properties'])} keys)")
        for key, prop in sorted(body["properties"].items()):
            line = f"  {key}: {prop.get('type')}"
            for lim in ("minLength", "maxLength"):
                if lim in prop:
                    line += f" {lim}={prop[lim]}"
            enum = enum_of(prop)
            if enum:
                line += f" enum={enum if len(enum) <= 15 else enum[:15] + ['...']}"
            print(line)


def attr(spec, name):
    for ptype, body in visible_types(spec).items():
        if name in body["properties"]:
            print(json.dumps(body["properties"][name], indent=2))
            return
    orderable = spec["properties"]["MPItem"]["items"]["properties"]["Orderable"]["properties"]
    print(json.dumps(orderable.get(name, f"{name} not found"), indent=2))


def validate(spec, feed_path):
    feed = json.load(open(feed_path, encoding="utf-8"))
    errors = []
    hdr_enum = spec["properties"]["MPItemFeedHeader"]["properties"]["version"].get("enum", [])
    version = feed.get("MPItemFeedHeader", {}).get("version")
    if hdr_enum and version not in hdr_enum:
        errors.append(f"header version {version!r} not in {hdr_enum}")
    orderable_spec = spec["properties"]["MPItem"]["items"]["properties"]["Orderable"]
    vtypes = visible_types(spec)
    for item in feed.get("MPItem", []):
        orderable = item.get("Orderable", {})
        sku = orderable.get("sku", "?")
        for req in orderable_spec.get("required", []):
            if req not in orderable:
                errors.append(f"{sku}: Orderable missing {req}")
        if "price" in orderable:
            errors.append(f"{sku}: price present in Orderable (never change Walmart price)")
        for key in orderable:
            if key not in orderable_spec["properties"]:
                errors.append(f"{sku}: Orderable.{key} not in spec (belongs in Visible?)")
        for ptype, attrs in item.get("Visible", {}).items():
            if ptype not in vtypes:
                errors.append(f"{sku}: product type {ptype!r} not in this spec file")
                continue
            props = vtypes[ptype]["properties"]
            for key, val in attrs.items():
                if key not in props:
                    errors.append(f"{sku}: Visible.{key} not in spec")
                    continue
                p = props[key]
                if p.get("type") == "array" and not isinstance(val, list):
                    errors.append(f"{sku}: {key} must be an array")
                if p.get("type") == "string" and not isinstance(val, str):
                    errors.append(f"{sku}: {key} must be a string")
                enum = enum_of(p)
                vals = val if isinstance(val, list) else [val]
                if enum:
                    bad = [v for v in vals if v not in enum]
                    if bad:
                        errors.append(f"{sku}: {key} values {bad} not in enum")
                for v in vals:
                    if isinstance(v, str):
                        lim = p.get("maxLength") or p.get("items", {}).get("maxLength")
                        if lim and len(v) > lim:
                            errors.append(f"{sku}: {key} longer than {lim}")
                        if "—" in v:
                            errors.append(f"{sku}: {key} contains an em dash")
                if key == "productName" and isinstance(val, str) and len(val) > 90:
                    errors.append(f"{sku}: productName is {len(val)} chars (keep <= 90)")
    print("\n".join(errors) if errors else "OK: feed matches spec")
    return not errors


if __name__ == "__main__":
    spec = load_spec(sys.argv[1])
    if "--validate" in sys.argv:
        sys.exit(0 if validate(spec, sys.argv[sys.argv.index("--validate") + 1]) else 1)
    elif "--attr" in sys.argv:
        attr(spec, sys.argv[sys.argv.index("--attr") + 1])
    else:
        summary(spec)
