# Contacts API guide

## Source and verification status

Contracts were inspected on 2026-09-09 using the official
[OpenAPI](https://apireference.getresponse.com/open-api.json) and
[API documentation](https://apidocs.getresponse.com/v3).
Live contact-maintenance and import scenarios are recorded in the repository's
`tests/getresponse-contacts-skill/LIVE_RESULTS.md`. Treat untested schema variants as documented
contracts, not live-verified behavior.

`openapi.json` contains only supported operations and their transitive component dependencies.
Search it by path or operationId instead of reading the entire schema for every task.

## Connection

Standard base URL: `https://api.getresponse.com/v3`.
Use `X-Auth-Token: api-key <key>` or OAuth `Authorization: Bearer <token>`.
Every request sends `X-Request-Source: getresponse/getresponse-contacts-skill@1.0.0`.
JSON bodies need `Content-Type: application/json`.
MAX needs the account's confirmed base URL and `X-Domain`; never guess the region/domain.
Keep keys in environment variables or the platform credential store, not generated files or logs.
Do not forward credentials to an arbitrary response URL; use the configured API host and IDs.

## Supported operations and risk

| Operations | Purpose | Risk and verification |
|---|---|---|
| `GET /contacts`, `GET /contacts/{contactId}` | Find and inspect active contacts | Low; exact match and all relevant pages |
| `POST /contacts`, `POST /contacts/batch` | Add contacts | High; async, GET-first, bounded verification |
| `POST /contacts/{contactId}` | Update, move, replace collections | Medium; high for moves/bulk replacement; fresh read and verify |
| `DELETE /contacts/{contactId}` | Remove a contact | High; exact authorized target, verify absence |
| `POST /contacts/{contactId}/tags` | Add tag assignments | Medium; preserve other tags, verify |
| `POST /contacts/{contactId}/custom-fields` | Add/update field values | Medium; preserve other fields, verify |
| `GET /campaigns`, `GET /campaigns/{campaignId}`, `POST /campaigns` | Resolve/create supporting lists | Low reads; medium creation, GET-first and verify |
| `GET /tags`, `GET /tags/{tagId}`, `POST /tags` | Resolve/create tag definitions | Low reads; medium creation, GET-first and verify |
| `GET /custom-fields`, `GET /custom-fields/{customFieldId}`, `POST /custom-fields` | Resolve/create field definitions | Low reads; medium creation, validate type and verify |
| `GET /imports`, `GET /imports/{importId}`, `POST /imports` | Track/schedule add-and-update imports | Medium reads; high submission, job reconciliation |
| `GET /gdpr-fields`, `GET /gdpr-fields/{gdprFieldId}` | Inspect consent definitions | Low; read only |
| `GET /contacts/{contactId}/consents` | Inspect grants and history | Low; read only, no inferred grants |

## Resolution and pagination

Use the client's query encoder (curl `--get --data-urlencode`, with `--globoff`). Encode both
keys and values, including brackets and literal `+` in email addresses. Contact lookup:

`GET /contacts?query[email]=…&query[campaignId]=…&additionalFlags=exactMatch&page=1&perPage=100`

Without `additionalFlags=exactMatch`, email/name filters can return partial matches. Check the
returned email and campaign ID even when using that flag. Resolve list/tag/field names with
`query[name]`, then select a single exact case-insensitive match; do not pick the first result.
If an email occurs on several lists and none was specified, present the lists and ask.
Do not merge these distinct contact memberships automatically.

List endpoints use `page` and `perPage` (1–1000, default 100). Follow documented pagination
headers where present, otherwise advance until a short/empty page. A failed or capped scan is
incomplete, not proof of absence. For large tasks agree a scope/budget before scanning.
Cache resolved IDs within the task. Prefer one scoped paginated scan to one lookup per CSV row.
Live `/contacts` accepted `perPage=0` and a nonnumeric value with HTTP 200; validate pagination
locally rather than relying on server rejection. An unsupported `query[...]` filter returned 400.
`/contacts` supports email, name, campaignId, origin, createdOn and changedOn filters, plus
documented sorting. It does not expose tag/custom-field query filters. For a small explicit
list, inspect fetched details locally; for advanced segment selection use the separate skill.

## Supporting resources

Create missing resources only when the user requested creation, not because lookup returned no
match. Verify returned IDs with the detail GET. Creation examples:

```json
{"name":"Customer onboarding"}
```

`POST /campaigns`: name is 3–64 characters; disallows emojis and `/`, `\`, `@`, `[` and `]`.
Omit opt-in settings unless the user explicitly chose them. No sender lookup is required for
the documented minimal list payload. Existing list settings are not modified by this skill.

```json
{"name":"vip_customer"}
```

`POST /tags`: name matches `^[_a-zA-Z0-9]{2,64}$`. Existing tag rename is deprecated/no-op
and is not supported. Detachment never requires deleting the global tag.

```json
{"name":"customer_tier","type":"string","format":"text","hidden":"false","values":[]}
```

`POST /custom-fields`: requires name, type, format, hidden, values. Name uses lowercase letters,
digits, underscores and must not be a reserved merge word (see schema). `hidden` is a string
boolean. Select formats require allowed values; validate the documented format/type combination.
When reusing a definition, compare `valueType`/`type`, `format`/legacy `fieldType`, and allowed
values. Stop on incompatible definitions; never change an account-wide definition to fit an
import. Contact field values use arrays of strings, including numeric/date values.

## Errors and request budgets

Use sequential mutations by default. Read rate-limit headers, including `X-RateLimit-Remaining`
and `X-RateLimit-Reset`, and respect endpoint-specific limits in [imports](imports.md).
Do not infer a universal account quota from another skill's measurements.

| Response | Action |
|---|---|
| `400` | Inspect validation context; correct only a known input error, never invent values |
| `401` / `403` | Stop; resolve credentials or access before retrying |
| `404` | Re-resolve ID/scope; a missing active contact is not proof of a global erasure |
| `409` on create | Read again; reuse only the exact compatible resource. Report existing contact separately; requested updates are not satisfied merely by existence |
| `409` on update/move/import | Report conflict; inspect destination membership/job state, do not treat as success |
| `429` | Read `Retry-After` (seconds or HTTP date), pause; fallback 5 seconds when missing. Retry a safe GET at most twice, then report blocked |
| Timeout / `5xx` | Retry safe GET at most twice with backoff; for writes reconcile state first and report uncertain if unprovable |

A known rejected mutation may be retried once after the server's wait if authorization still
covers it and the target is unchanged. Do not replay a write with uncertain acceptance. Waiting
does not extend import polling beyond its deadline. No stress probing during normal work.
