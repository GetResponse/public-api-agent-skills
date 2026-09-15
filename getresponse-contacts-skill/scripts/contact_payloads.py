#!/usr/bin/env python3
"""Build minimal contact collection replacements from a complete fresh GET detail.

Offline only. JSON input on stdin, payload on stdout; failures never echo contact data.
"""
import argparse
import json
import sys


def removal_payload(contact, collection, ids):
    if collection not in ("tags", "customFieldValues"):
        raise ValueError("Unsupported collection")
    if not isinstance(contact, dict) or not isinstance(contact.get(collection), list):
        raise ValueError("A complete contact detail with the affected collection is required")
    if not ids or any(not isinstance(i, str) or not i.strip() for i in ids):
        raise ValueError("Provide non-empty IDs to remove")
    key = "tagId" if collection == "tags" else "customFieldId"
    seen, retained = set(), []
    for item in contact[collection]:
        if not isinstance(item, dict) or not isinstance(item.get(key), str) or not item[key]:
            raise ValueError("Collection has a missing or invalid ID")
        if item[key] in seen:
            raise ValueError("Collection has duplicate IDs; fetch an unambiguous detail")
        seen.add(item[key])
        writable = {key: item[key]}
        if collection == "customFieldValues":
            if "value" in item and "values" in item and item["value"] != item["values"]:
                raise ValueError("Conflicting value representations")
            value = item.get("value", item.get("values"))
            if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
                raise ValueError("Field values must be arrays of strings")
            writable["value"] = list(value)
        if item[key] not in ids:
            retained.append(writable)
    return {collection: retained} if seen.intersection(ids) else {}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["remove-tags", "remove-fields"])
    parser.add_argument("--ids", nargs="+", required=True)
    args = parser.parse_args()
    try:
        collection = "tags" if args.action == "remove-tags" else "customFieldValues"
        payload = removal_payload(json.load(sys.stdin), collection, args.ids)
    except (ValueError, TypeError):
        parser.exit(2, "Cannot build replacement: invalid or incomplete contact snapshot/IDs.\n")
    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
