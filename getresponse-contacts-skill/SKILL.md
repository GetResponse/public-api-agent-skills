---
name: getresponse-contacts-skill
description: >
  Manage GetResponse contacts, tags, custom-field values, imports and consent history via API v3.
  Triggers: create or update contacts, supporting lists/definitions and import verification.
  Excludes segments, newsletter delivery and autoresponder setup.
license: MIT
metadata:
  version: "1.0.0"
  author: GetResponse
allowed-tools:
  - WebFetch
  - WebSearch
  - Bash(curl *)
  - Bash(python3 *)
  - http_request
---

# GetResponse Contacts Skill

**UTILITY SKILL. INVOKES: none.**

## USE FOR:

- Find, add, update, move or delete contacts.
- Assign/remove contact tags or custom-field values; read consent history.
- Import contacts; create supporting resources.

## DO NOT USE FOR:

- Saved segments or advanced segment searches (`/search-contacts`).
- Newsletter delivery, autoresponder setup, copying, exports or activity reports.
- Consent writes, list settings, global definition edits/deletion, blocklists or suppressions.

Explain exclusions.

## Rules

1. Resolve exact email + list or verified contact ID; ask about ambiguity. GET-first before
   creation; create only requested resources.
2. Preserve unrelated data: general updates replace supplied collections; dedicated endpoints
   upsert. [Contact changes](references/contact-changes.md) covers removals preserving other data.
3. Preview exact targets and impact for moves, deletion and bulk changes. Obtain authorization
   when not already supplied. Preserve opt-in settings; never infer consent or cycle enrollment.
   Consider existing automation effects.
4. Verify writes. `202` or an import's `201` is acceptance, not completion. Follow
   [imports](references/imports.md) for bounded polling, partial results and sampling limits.

## Error handling

Use configured credentials; ask when missing. Send `X-Auth-Token: api-key <key>`
(or configured OAuth) and `X-Request-Source: getresponse/getresponse-contacts-skill@1.0.0`.
Never expose keys. Honor `429`/`Retry-After`, bound retries, reconcile `409`; do not replay uncertain
writes. [API guide](references/api-guide.md) covers authentication, errors and MAX.

## Examples

[Examples](assets/examples.md). [OpenAPI](openapi.json): schemas.
