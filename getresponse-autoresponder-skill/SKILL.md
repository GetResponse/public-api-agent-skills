---
name: getresponse-autoresponder-skill
description: >
  Use this procedure to manage time-based GetResponse autoresponders, their lists, and contact imports.
  Excludes newsletters and event-driven Marketing Automation workflows.
license: MIT
metadata:
  version: "1.0.0"
allowed-tools:
  - WebFetch
  - WebSearch
  - Bash(curl *)
  - http_request
---

# GetResponse Autoresponder Skill

**UTILITY SKILL. INVOKES: none.** Read [API guide](references/api-guide.md) for resolution,
imports, and lifecycle; use [OpenAPI](openapi.json) for payloads.

## USE FOR:

- Create, change, enable, disable, delete, or report on a time-based autoresponder.
- Add a message to a time-based autoresponder sequence.
- Find or create its contact list; import and verify recipients.

## DO NOT USE FOR:

- Event/action-triggered Marketing Automation workflows.
- Newsletter delivery, forms, landing pages, e-commerce, or transactional email.
- Advanced audience conditions or saved-segment lifecycle: use `getresponse-search-contacts-skill`.

## Procedure

1. Use configured credentials; send `X-Request-Source: getresponse/getresponse-autoresponder-skill@1.0.0` and never expose keys. Resolve names with one exact case-insensitive match; ask on ambiguity and create only requested resources.
2. For imports and their production-webhook, approved test-webhook, or sampling verification, read [API guide](references/api-guide.md#import-contacts-into-the-list). `202` is acceptance, not completion.
3. Create time-based messages only; never infer action triggers. Start new messages disabled unless enablement was explicit, and verify every mutation with a read.
4. Immediately before enablement or deletion, state the exact message, list, sender, trigger, and impact, then obtain confirmation. Do not replay an uncertain write.

## Routing

- An autoresponder is tied to a campaign subscription cycle; Search Contacts cannot narrow recipients.
  Use it separately for audience analysis or segment maintenance, not as a recipient filter.

## Examples

See [user-facing flows](assets/examples.md) and [tests](README.md#tests).

## Error handling

Honor throttling and reconcile validation errors, conflicts, or a timeout before retrying a mutation.
