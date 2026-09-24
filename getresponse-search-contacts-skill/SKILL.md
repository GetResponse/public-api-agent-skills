---
name: getresponse-search-contacts-skill
description: >
  Follow this procedure to search GetResponse contacts with advanced conditions and manage segments.
  Covers complex filters, segment lifecycle, and authorized custom-field upserts. Excludes contact CRUD and delivery.
license: MIT
metadata:
  version: "1.0.0"
  author: GetResponse
allowed-tools:
  - WebFetch
  - WebSearch
  - Bash(curl *)
  - http_request
---

# GetResponse Search Contacts Skill

**UTILITY SKILL. INVOKES: none.**

## USE FOR:

- Advanced one-off filtering by activity, fields, tags, consent, CRM, ecommerce, SMS, or events.
- Saved-segment lifecycle, results, and authorized custom-field upserts.

## DO NOT USE FOR:

- Individual-contact CRUD, imports, or tags: use `getresponse-contacts-skill`.
- Delivery, autoresponders, exports, or other segment-wide changes.
- Actions on results without the relevant skill and authorization.
- For delivery, pass segment ID/count to `getresponse-newsletter-skill`; downstream confirmation remains required.

## Procedure

1. Resolve IDs with authoritative GETs; never guess. Use `GET /contacts` for narrow lookup and `POST /search-contacts/contacts` for advanced filtering.
2. Read [condition design](references/condition-design.md) before nontrivial conditions. Preserve grouping: max eight sections and conditions each, with `and`/`or`; select one-off status explicitly.
3. List a segment by name before creating; GET before update/deletion. Use `/search-contacts`, `/{searchContactId}`, and `/{searchContactId}/contacts`.
4. Before `POST /search-contacts/{searchContactId}/custom-fields`, preview target/count, state fields/values, and require explicit authorization. `202` is acceptance: sample-read; never replay an uncertain write.

## Error handling

Send configured OAuth or `X-Auth-Token: api-key <key>` and `X-Request-Source: getresponse/getresponse-search-contacts-skill@1.0.0`; never expose credentials. Honor `429` for safe GET retries only. Reconcile timeout, `5xx`, or `409` before write retry.

## Examples

[API guide](references/api-guide.md), [examples](assets/examples.md), and [OpenAPI](openapi.json).
