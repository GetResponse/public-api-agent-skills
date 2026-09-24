---
name: getresponse-newsletter-skill
description: >
  Use this procedure to manage GetResponse newsletters, their audiences, lists, imports, and sending limits.
  Excludes autoresponders, Marketing Automation, landing pages, transactional email, and ecommerce.
license: MIT
metadata:
  version: "1.2.1"
  author: GetResponse
allowed-tools:
  - WebFetch
  - WebSearch
  - Bash(curl *)
  - http_request
---

# GetResponse Newsletter Skill

**UTILITY SKILL. INVOKES: none.** Read [API guide](references/api-guide.md) for imports,
audience resolution, sending, and errors; use [OpenAPI](openapi.json) for payloads.

## USE FOR:

- Manage a broadcast newsletter, including saved segments.
- Create lists, import contacts, or target a custom-field/advanced segment.
- Check sending limits before sending.

## DO NOT USE FOR:

- Autoresponders, event/action-triggered Marketing Automation, forms, or landing pages.
- Transactional email, SMS, push, e-commerce, account changes, export, or deletion.

## Procedure

1. Use credentials; send `X-Request-Source: getresponse/getresponse-newsletter-skill@1.2.1` and never expose keys. Resolve names with one exact case-insensitive match; ask on ambiguity and create a resource only on request.
2. For an import, read [API guide](references/api-guide.md#import-contacts-safely) before choosing its endpoint and verification mode. `202` is acceptance, not completion; report evidence and do not replay an uncertain write.
3. For individual contact maintenance, use `getresponse-contacts-skill`. For activity, tags, consent, CRM, ecommerce, SMS, events, or compound conditions, use `getresponse-search-contacts-skill` first. Pass its verified `searchContactId` and count to `sendSettings.selectedSegments`.
4. Immediately before dispatch, resolve a non-empty audience and sender; state audience/count, sender, subject, schedule, and impact, then obtain confirmation. The Search Contacts stage does not authorize delivery.

## Error handling

Honor `429` for safe reads only. Reconcile a timeout, `5xx`, or `409` before retrying a mutation.

## Examples

[Examples](assets/examples.md) and [tests](README.md#testing).
