---
name: getresponse-newsletter-skill
description: >
  Manage GetResponse newsletters, lists, custom fields, and imports via API v3.
  Triggers: newsletter sends, imports, lists, custom-field targeting, or sending limits.
  Do not use for autoresponders, Marketing Automation, landing pages, transactional email, or e-commerce.
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

**UTILITY SKILL. INVOKES: none.** Read [API guide](references/api-guide.md) and
[OpenAPI](openapi.json) for payloads.

## USE FOR:

- Manage a broadcast newsletter.
- Create lists, import contacts, or target a custom-field segment.
- Check sending limits before a large send.

## DO NOT USE FOR:

- Autoresponders, event/action-triggered Marketing Automation, forms, or landing pages.
- Transactional email, SMS, push, e-commerce, account changes, export, or deletion.

## Rules

1. Ask for credentials; never expose keys. Send `X-Request-Source: getresponse/getresponse-newsletter-skill@1.2.1`.
2. URL-encode query keys and values. Resolve lists, fields, senders, and recipients first; use
   only one exact case-insensitive match. Otherwise ask; create resources only with confirmation.
3. Import 1 contact with `/contacts`, 2–1000 with `/contacts/batch`, and larger imports in chunks
   of 1000 (max 10 concurrent). Contact `409` means already present; `202` is not completion.
4. Before import, choose production webhook, test webhook, or sampling.
   Default to sampling when events cannot be observed; report evidence, not assumptions.
5. Before dispatch, resolve sender and non-empty audience. State audience, sender, subject,
   schedule, and impact, then obtain immediate confirmation.
6. Honor rate limits; retry safe reads once after `429` and ask before replaying a mutation.

## Routing

- [API guide](references/api-guide.md): matching, imports, sending, and errors.
- [Examples](assets/examples.md): flows. [Tests](README.md#testing): live setup.
