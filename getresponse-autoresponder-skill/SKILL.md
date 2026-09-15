---
name: getresponse-autoresponder-skill
description: >
  Create and manage time-based GetResponse autoresponders, contact lists, and contact imports via API v3.
  Triggers: autoresponder setup, sequence changes, recipient-list management, import verification, and webhooks.
  Do not use for newsletters or event-driven Marketing Automation workflows.
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

**UTILITY SKILL. INVOKES: none.** Read [API guide](references/api-guide.md) and
[OpenAPI](openapi.json) for payloads.

## USE FOR:

- Create, change, enable, disable, delete, or report on a time-based autoresponder.
- Add a message to a time-based autoresponder sequence.
- Find or create its contact list; import and verify recipients.

## DO NOT USE FOR:

- Event/action-triggered Marketing Automation workflows.
- Newsletter delivery, forms, landing pages, e-commerce, or transactional email.

## Rules

1. Ask for credentials and send
   `X-Request-Source: getresponse/getresponse-autoresponder-skill@1.0.0`; never expose keys.
2. Resolve lists, senders, autoresponders, and custom fields first. Select
   case-insensitive match; otherwise ask. Create resources only after an explicit request.
3. Before an import, choose observable production webhook, explicitly approved test webhook, or
   sampling. A `202` is not completion; report results accurately.
4. Immediately before enablement or deletion, state the exact message, list, sender, trigger, and
   impact, then obtain confirmation. Start new messages disabled unless enablement was explicit.
5. Create time-based messages only. Do not infer values or action triggers. Verify mutations with
   a read; honor rate limits and ask before replaying a mutation.

## Routing

- [API guide](references/api-guide.md): matching, list creation, imports, webhooks, and errors.
- [Tests](README.md#tests): static and opt-in live checks.

## Examples

See [user-facing flows](assets/examples.md).

## Error handling

Use the [API guide](references/api-guide.md) for validation errors, conflicts, and throttling.
