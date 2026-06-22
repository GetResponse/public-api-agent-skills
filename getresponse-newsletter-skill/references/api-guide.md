# GetResponse API v3 — Reference Guide for Skill

Base URL: `https://api.getresponse.com/v3`

All requests require the header:
```
X-Auth-Token: api-key YOUR_API_KEY
Content-Type: application/json
X-Request-Source: getresponse/getresponse-newsletter-skill@1.0.0
```

> **`X-Request-Source`** identifies agent traffic. Value format: `getresponse/{name}@{version}` (version is semver `major.minor.patch`). Agents using this skill must always include this header.

---

## Rate Limits & Throttling

GetResponse throttles API calls per API key:

- **Per second**: max **80 requests/second**
- **Per time frame**: max **30,000 requests per 10-minute window**
- **Time frame**: 10 minutes — limits reset at the end of each window
- **Response headers** on every call:
  - `X-RateLimit-Limit` — per-second limit (80)
  - `X-RateLimit-Remaining` — calls left in the current second
  - `X-RateLimit-Reset` — seconds until the current window resets
- If `X-RateLimit-Remaining` = 0 → pause before the next call
- For parallel operations: **max 10 concurrent requests** (recommended: use up to 10)
- For large parallel operations (>10 concurrent), spread requests in waves of 10 to avoid hitting 80 req/s

### Handling HTTP 429 (Rate Limit Exceeded)

When a request returns HTTP 429:

1. Read the `Retry-After` response header — it contains the number of seconds to wait (typically `1`)
2. Inform the user: *"Rate limit reached — pausing for Ns and resuming."*
3. Sleep exactly `Retry-After` seconds (default to 1s if header is absent)
4. Retry the failed request — it should succeed with HTTP 200/201/202

**Headers present on every 429 response (confirmed on live API):**
```
HTTP/2 429
Retry-After: 1
X-RateLimit-Limit: 80
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1 seconds
```

The 429 rate limit is per-second (80 req/s). The per-window limit (30,000/10 min) rarely triggers in normal skill usage.

### Batch Contact Limits
- `/contacts/batch` accepts a maximum of **1000 contacts per request**
- For >1000 contacts: split into 1000-contact chunks, process up to 10 chunks in parallel
- Check account-level sending limits with `GET /accounts/sending-limits` before bulk sends

---

## Campaigns (Contact Lists)

A "campaign" in GetResponse is a contact list / audience segment.

### List campaigns
```
GET /campaigns?query[name]=<name>&page=1&perPage=100
```
Returns array of `Campaign` objects. Filter by name to check existence.

### Create campaign
```
POST /campaigns
```
Body:
```json
{
  "name": "my-campaign",
  "languageCode": "en",
  "optinTypes": {
    "api": "single"
  }
}
```
- `name` must be unique across the account
- `optinTypes.api: "single"` skips double opt-in for API-added contacts
- Returns `Campaign` with `campaignId`

### Get campaign by ID
```
GET /campaigns/{campaignId}
```

---

## Custom Fields

Custom fields are account-level definitions. They must exist before being referenced in contact data.

### List custom fields
```
GET /custom-fields?query[name]=<name>&page=1&perPage=100
```
Use `query[name]` to check if a field already exists.

### Create custom field
```
POST /custom-fields
```
Body:
```json
{
  "name": "company_name",
  "type": "text",
  "hidden": "false",
  "values": []
}
```
- `name`: lowercase, underscores only, no spaces, max 64 chars, must be unique
- `type` options: `text`, `phone`, `number`, `date`, `datetime`, `single_select`, `multi_select`
- `hidden`: **always required** — use `"false"` for visible fields
- `values`: **always required** — use `[]` for `text`/`phone`/`number`/`date` types; provide options for `single_select`/`multi_select`
- Returns `CustomField` with `customFieldId`

### Custom field value format in contacts
Always wrap values in an array:
```json
{ "customFieldId": "abc123", "value": ["my value"] }
```
For multi-select: `"value": ["val1", "val2"]`

---

## Contacts

### List / search contacts
```
GET /contacts?query[email]=<email>&query[campaignId]=<id>&page=1&perPage=100
```
Add `additionalFlags=customFieldValues` to include custom field data in response.

### Add single contact
```
POST /contacts
```
Body:
```json
{
  "email": "user@example.com",
  "name": "Jane Doe",
  "campaign": { "campaignId": "abc123" },
  "customFieldValues": [
    { "customFieldId": "field1", "value": ["Engineering"] }
  ]
}
```
- Response **202** = accepted (async processing, no body)
- Response **409** = contact already exists in this campaign (not an error — treat as success)
- Response **400** = validation failure (check `message` field)

### Batch import contacts (up to 1000)
```
POST /contacts/batch
```
Body:
```json
{
  "campaignId": "abc123",
  "contacts": [
    {
      "email": "a@example.com",
      "name": "Alice",
      "customFieldValues": [
        { "customFieldId": "field1", "value": ["Sales"] }
      ]
    },
    {
      "email": "b@example.com",
      "name": "Bob"
    }
  ]
}
```
- Response **202** = batch accepted
- Max 1000 contacts per request
- For >1000: chunk into groups of 1000, call in parallel (max 10 concurrent)

### Update contact custom fields
```
POST /contacts/{contactId}/custom-fields
```
Body:
```json
{
  "customFieldValues": [
    { "customFieldId": "field1", "value": ["new value"] }
  ]
}
```
Upserts values — existing fields not listed are untouched.

---

## Async Contact Verification

All contact add endpoints (`POST /contacts`, `POST /contacts/batch`) return `202 Accepted` immediately. Contacts are processed asynchronously — they may appear within seconds or take up to several minutes.

Before proceeding to newsletter sending, ask the user which verification mode to use. Default timeout is **10 minutes** unless the user/agent specifies otherwise.

### Mode A — Production Webhook

> **Important:** GetResponse does **not** expose an API endpoint to register webhook URLs. The URL must be configured manually in the GetResponse web panel.

#### How to configure a webhook in GetResponse

1. Log in to the GetResponse dashboard.
2. Go to **Menu → Integrations & API → API** (or navigate directly to `https://app.getresponse.com/integrations/api`).
3. In the **Webhooks** section, click **Add new webhook**.
4. Enter the HTTPS URL that will receive events.
5. Under **Events**, enable **Contact subscribed** (this fires when a contact is successfully added to a list).
6. Click **Save**.

> The URL must be publicly reachable over HTTPS. GetResponse will send a POST request to this URL for each matching event.

Once configured, provide the webhook URL to the agent:

1. Ask the user to configure their webhook URL in GetResponse as described above, then provide that URL to the agent.
2. Wait for incoming `subscribe` events on the provided URL (timeout: 10 min default).
3. When expected contact count is reached or timeout expires → proceed.

#### Incoming callback payload (`contact-subscribed`):
```json
{
  "contactId": "abc123",
  "email": "user@example.com",
  "name": "Jane Doe",
  "campaignId": "camp456",
  "createdOn": "2026-01-01T12:00:00Z"
}
```
Reference: https://apidocs.getresponse.com/v3/payloads#contact-subscribed

### Mode B — Test Webhook (webhook.site)

⚠️ **GDPR warning**: contact emails pass through webhook.site (external US service). Use only for development/testing with non-production data.

1. `GET https://webhook.site/token` → get `uuid` and `url`
2. Instruct the user to paste the generated URL into **GetResponse Dashboard → Integrations → Webhooks** and confirm when done.
3. Poll `GET https://webhook.site/token/<uuid>/requests` every **15 seconds**
4. Count `subscribe` events; stop on expected count or timeout

### Mode C — Sampling with Exponential Backoff

Verify a small sample via `GET /contacts?query[email]=<email>` — never query all contacts individually.

**Sample size:**
| Contacts added | Sample | Max GET requests |
|---|---|---|
| 1–10 | all | ≤ 10 |
| 11–1000 | 5 distributed (first, ~25%, ~50%, ~75%, last) | 5 |
| >1000 (multi-batch) | 1 per batch, max 10 total | ≤ 10 |

**Backoff schedule (default ~10 min total):**
| Attempt | Wait | Elapsed |
|---|---|---|
| 1 | 5 s | 5 s |
| 2 | 15 s | 20 s |
| 3 | 30 s | 50 s |
| 4 | 60 s | ~2 min |
| 5 | 120 s | ~4 min |
| 6 | 300 s | ~9 min |
| 7 (max) | — | timeout |

- 100% sample visible → proceed
- Partial after 7 attempts → report count, proceed with warning
- Custom timeout: scale attempt count proportionally

### Skip verification entirely

Skip if newsletter targets the **whole campaign** (`selectedCampaigns`) and user confirms no verification needed. Inform user: *"Newsletter will be sent to all active contacts in the campaign at send time."*

---

## Newsletters

### List newsletters
```
GET /newsletters?query[status]=<status>&query[campaignId]=<id>
```
Status values: `scheduled`, `sending`, `sent`, `draft`, `error`

### Create and send newsletter
```
POST /newsletters
```
Body:
```json
{
  "subject": "Your subject here",
  "name": "internal-newsletter-name",
  "type": "broadcast",
  "content": {
    "html": "<!DOCTYPE html><html>...</html>",
    "plain": "Plain text fallback"
  },
  "fromField": {
    "fromFieldId": "from123"
  },
  "campaign": {
    "campaignId": "camp123"
  },
  "replyTo": {
    "fromFieldId": "from123"
  },
  "sendSettings": {
    "selectedCampaigns": ["camp123"]
  },
  "flags": ["openrate", "clicktrack"]
}
```

> **Important:** `campaign.campaignId` at the root level is **required** — it sets the campaign context for unsubscribe links and sender identity. Without it the API returns 400.

#### sendSettings options (use one or combine):
- `selectedCampaigns`: array of plain campaignId **strings** (not objects) — send to all subscribed contacts in listed campaigns
- `selectedContacts`: array of plain contactId **strings** (not objects) — send to specific contacts
- `selectedSegments`: array of plain searchContactId **strings** (not objects) — send to contacts in a saved segment

#### Scheduling:
- Omit `sendOn` → send immediately
- Include `sendOn` with ISO 8601 datetime → schedule for future delivery

#### Response:
- **201** → success, returns `Newsletter` object with `newsletterId` and `status`
- `status` can be `scheduled`, `sending`, `sent`, or `draft`

### Get newsletter status
```
GET /newsletters/{newsletterId}
```

### Cancel newsletter
```
POST /newsletters/{newsletterId}/cancel
```
Stops a scheduled or in-progress send.

---

## From Fields (Sender Addresses)

Before sending a newsletter, you need a valid `fromFieldId`.

### List from fields
```
GET /from-fields?query[isDefault]=true&query[isActive]=true
```
Returns array of `FromField` objects. Pick `fromFieldId` from the default/active sender.

---

## Search Contacts (Ad-hoc Segment Queries)

Use this to find contacts by custom field value before targeting them in a newsletter.

### Ad-hoc search by conditions
```
POST /search-contacts/contacts?page=1&perPage=1000
```
Body:
```json
{
  "subscribersType": ["subscribed"],
  "sectionLogicOperator": "and",
  "section": [
    {
      "campaignIdsList": ["camp123"],
      "subscriberCycle": ["receiving_autoresponder", "not_receiving_autoresponder"],
      "subscriptionDate": "all_time",
      "logicOperator": "and",
      "conditions": [
        {
          "conditionType": "custom",
          "scope": "<customFieldId>",
          "operator": "is",
          "operatorType": "string_operator_list",
          "value": "target_value"
        }
      ]
    }
  ]
}
```

> **Important field notes:**
> - `campaignIdsList`: array of plain campaignId **strings** — required in every section
> - `subscriberCycle`: array of strings — required; use both `receiving_autoresponder` and `not_receiving_autoresponder` to include all contacts
> - `subscriptionDate`: required enum string — `"all_time"`, `"today"`, `"yesterday"`, `"last_7_days"`, `"last_30_days"`, `"this_week"`, `"last_week"`, `"this_month"`, `"last_month"`, `"last_2_months"`, `"custom"`
> - `conditionType`: use `"custom"` for custom field filters (not `"custom_field"`)
> - `scope`: the `customFieldId` of the field to filter on
> - `value`: plain string (not an array)
> - `operatorType`: `"string_operator"` for text fields, `"string_operator_list"` for select fields

#### conditionType values:
- `custom` — filter by a custom field value (use `scope` = customFieldId)
- `name` — filter by contact name
- `email` — filter by email address pattern
- `origin` — filter by subscription origin

#### operator values:
- `is`, `is_not`, `contains`, `not_contains`, `starts_with`, `ends_with`

Returns array of contacts with `contactId`, `email`, `name`, `campaign`.

To use results in newsletter `sendSettings`:
```json
"selectedContacts": ["id1", "id2"]
```

---

## Common Error Codes

| Code | Meaning |
|---|---|
| 1001 | Invalid API key |
| 1002 | Missing required field |
| 1003 | Field value too long |
| 1008 | Name already in use |
| 1010 | Invalid email format |
| 1021 | Contact already in campaign |

Full error reference: https://apireference.getresponse.com/

---

## Pagination

All list endpoints support:
- `page` (default: 1)
- `perPage` (default: 100, max: 1000)

Response headers include:
- `TotalCount` — total number of items
- `TotalPages` — total pages

To fetch all records, iterate pages until the response array has fewer items than `perPage`.
