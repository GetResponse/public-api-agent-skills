# GetResponse Autoresponders API guide

Base URL for standard accounts: `https://api.getresponse.com/v3`.

Every request needs `X-Auth-Token: api-key <key>` and
`X-Request-Source: getresponse/getresponse-autoresponder-skill@1.0.0`. OAuth uses
`Authorization: Bearer <token>` instead. GetResponse MAX requires its account-specific base URL
plus `X-Domain: <domain>`.

## Resource resolution

| Need | Request | Select safely |
|---|---|---|
| Autoresponder | `GET /autoresponders?query[name]=…` | exact name match; otherwise ask |
| Campaign/list | `GET /campaigns?query[name]=…` | exact name match; otherwise ask |
| Known campaign ID | `GET /campaigns/{campaignId}` | verify the selected test or user-supplied list |
| Sender / reply-to | `GET /from-fields` | use an approved, user-selected address |
| Details | `GET /autoresponders/{autoresponderId}` | use the ID selected above |

Encode query keys and values on the wire: `query[name]` becomes `query%5Bname%5D`; encode spaces,
`&`, `+`, `@`, brackets, and non-ASCII values. Prefer the HTTP client's parameter encoder.

## Create a contact list

When an explicitly requested list has no exact existing match, ask whether to create the new list.
After confirmation, call `POST /campaigns` with its requested unique name. `name` is required and
must be 3–64 characters; it cannot contain `/`, `\\`, `@`, `[` or `]`. The response supplies the
`campaignId` to use in the autoresponder payload. Do not create a list merely because a search had
no result.

For API-created contacts added later by another process, the user may choose an API opt-in setting,
but this skill must not select or change it by default.

## Import contacts into the list

Use `POST /contacts` for one contact and `POST /contacts/batch` for 2–1000 contacts. A contact
needs `email` and the selected campaign reference; `name` and `customFieldValues` are optional.
For a batch, put the destination `campaignId` at the top level and each contact in `contacts`.

```json
{
  "campaignId": "CAMPAIGN_ID",
  "contacts": [
    { "email": "ada@example.com", "name": "Ada Lovelace" },
    { "email": "grace@example.com", "name": "Grace Hopper" }
  ]
}
```

Both endpoints return `202 Accepted`; this only acknowledges asynchronous processing. Choose a
verification mode before submitting the import. The default timeout is 10 minutes, unless the user
chooses another bounded timeout. `409` for an individual contact means it already exists; do not
resend it automatically. For imports exceeding 1,000 contacts, chunk by 1,000 and keep an
email-to-chunk record so partial failures are reportable.

When custom field values are supplied, first resolve each `customFieldId` through
`GET /custom-fields?query[name]=…`. Only reuse an exact-name field whose type and allowed values
fit the supplied data; otherwise ask the user whether to use an existing field or create one.

### Mode A — production webhook

Use this only when the user has a publicly reachable HTTPS endpoint and the agent can inspect its
received events through an approved log, queue, or user-provided event data. GetResponse does not
offer an API endpoint to register webhook URLs. The user must configure it manually in the
GetResponse dashboard: **Menu → Integrations & API → API → Webhooks → Add new webhook**, enter
the endpoint URL, enable **Contact subscribed**, and save.

Ask the user to confirm the URL and event selection before starting the import. Count the received
`subscribe` callbacks for the imported contacts until the expected count or the timeout. If the
agent cannot observe those callbacks, switch to Mode C; never claim that merely configuring a URL
verified the import.

### Mode B — test webhook (webhook.site)

This is for development and test contacts only. Explain before use that contact email addresses are
sent to an external third-party service and may leave the user's applicable data-processing region;
do not use it for production or personal data without explicit approval. Create a unique test URL
with `GET https://webhook.site/token`, give the resulting URL to the user to configure in the
GetResponse dashboard using the same **Contact subscribed** event, and wait for confirmation.
Then poll `GET https://webhook.site/token/<uuid>/requests` every 15 seconds, counting callbacks
whose payload indicates `type: subscribe`. Stop at the expected count or the chosen timeout and
report the number actually confirmed.

### Mode C — sampling (default)

Select all contacts for imports of 1–10, five representative contacts for imports of 11–1,000, and
one contact per chunk (at most ten) for larger imports. Query each selected address through
`GET /contacts?query[email]=…`; encode both the query key and email value. Use waits of 5, 15, 30,
60, 120, and 300 seconds, stopping after the next check or at the 10-minute timeout. Report partial
verification accurately; a visible sample is evidence for the import, not proof that every record
was accepted.

## Create and update

`POST /autoresponders` creates a message (`201`).
`POST /autoresponders/{autoresponderId}` updates it (`200`). Use the complete object returned by a
preceding detail request as the starting point for an update; retain fields that must not change.

At minimum, a new message needs `status`, `subject`, `content`, `sendSettings`, and
`triggerSettings`. Use explicit `campaignId`, `fromField`, and `replyTo` whenever the account has
more than one applicable option.

```json
{
  "name": "Welcome — day 0",
  "subject": "Welcome",
  "campaignId": "CAMPAIGN_ID",
  "status": "disabled",
  "fromField": { "fromFieldId": "FROM_FIELD_ID" },
  "replyTo": { "fromFieldId": "REPLY_TO_ID" },
  "content": {
    "html": "<h1>Welcome</h1><p>Thanks for joining us.</p>",
    "plain": "Welcome\n\nThanks for joining us."
  },
  "sendSettings": { "type": "signup" },
  "triggerSettings": { "type": "onday", "dayOfCycle": 0 }
}
```

`sendSettings.type` is one of `signup`, `immediately`, `delay`, or `custom`; each variant has
additional required fields. Read its schema in `openapi.json` before composing a non-`signup`
request. `triggerSettings.type` supports legacy `onday` only. Do not send deprecated action-based
trigger fields.

## Status and deletion

Use the same update endpoint to set `status` to `enabled` or `disabled`; enablement requires an
immediate pre-flight confirmation. `DELETE /autoresponders/{autoresponderId}` returns `204`; only
call it after a final confirmation that includes the exact ID and name.

## Statistics

Use `GET /autoresponders/{autoresponderId}/statistics` for one message or
`GET /autoresponders/statistics` for account-level data. Inspect `openapi.json` for supported
filters before issuing the request; do not guess statistic dimensions or date filters.

## Limits and errors

The documented account limit is 80 requests per second, 30,000 requests per 10-minute window, and
at most 10 parallel requests. Inspect `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and
`X-RateLimit-Reset` on every response. On `429`, wait according to `Retry-After` if available,
otherwise until the reset header (or use bounded backoff for reads). Never automatically replay a
write. `400` means validate fields; `401` means stop and request valid credentials; `404` means
the selected resource no longer exists; `409` means stop and resolve the conflict with the user.
