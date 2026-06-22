---
name: getresponse-newsletter-skill
description: >
  Use this skill to manage GetResponse email marketing operations via the GetResponse API v3.
  Triggers: whenever the user wants to (1) add or import contacts to a GetResponse campaign/list,
  (2) create or find a campaign (contact list), (3) define or check custom fields for contacts,
  (4) send a newsletter or email campaign to contacts selected by campaign or custom field values,
  (5) check sending limits before dispatching bulk emails.
  Do NOT use for landing pages, autoresponders, webforms, transactional emails, or e-commerce features.
version: 1.0.0
license: MIT
authors:
  - name: GetResponse
allowed-tools:
  - WebFetch
  - WebSearch
  - Bash(curl *)
  - http_request
---

# GetResponse Newsletter Skill

## Overview

This skill lets you interact with the **GetResponse API v3** to:
1. **Find or create a campaign** (contact list/audience)
2. **Ensure custom fields exist** before adding contacts that use them
3. **Add contacts** (single or batch, with optional custom field values) to a campaign, then **verify the async import** via webhook (if user has one configured) or sampling with exponential backoff
4. **Send a newsletter** with agent-defined HTML content to a campaign or a custom-field-filtered segment

API reference: `references/api-guide.md`
OpenAPI spec: `openapi.json`

---

## Authentication

Every API request requires the header:
```
X-Auth-Token: api-key YOUR_API_KEY
X-Request-Source: getresponse/getresponse-newsletter-skill@1.0.0
```

Ask the user for their API key if not provided. Never hardcode or log API keys.

---

## Workflow

Always execute steps in this order. Do not skip steps.

### Step 1 — Resolve Campaign

**Goal:** obtain a valid `campaignId`.

1. Call `GET /campaigns?query[name]=<campaign_name>` (use `listCampaigns`).
2. If the response array contains a matching campaign → use its `campaignId`.
3. If not found → create it with `POST /campaigns` (use `createCampaign`):
   - Required field: `name`
   - Recommended: set `optinTypes.api` to `"single"` so API-added contacts skip double opt-in
   - Save the returned `campaignId`.

### Step 2 — Resolve Custom Fields (skip if contacts have no custom fields)

For **each** custom field name referenced in the contact data:

1. Call `GET /custom-fields?query[name]=<field_name>` (use `listCustomFields`).
2. If found → record its `customFieldId`.
3. If not found → create with `POST /custom-fields` (use `createCustomField`):
   - Required: `name` (lowercase, underscores, no spaces), `type` (use `"text"` for strings)
   - Always include `"hidden": "false"` and `"values": []` — the API requires both fields even for `text` type
   - Save the returned `customFieldId`.

Run these checks in parallel when there are multiple custom fields to resolve.

### Step 3 — Add Contacts

Choose the appropriate method based on contact count:

#### Single contact (1 contact):
Use `POST /contacts` (use `createContact`):
```json
{
  "email": "user@example.com",
  "name": "First Last",
  "campaign": { "campaignId": "<campaignId>" },
  "customFieldValues": [
    { "customFieldId": "<id>", "value": ["<value>"] }
  ]
}
```
Response 202 = accepted (async). Response 409 = already exists (not an error, continue).

#### Multiple contacts (2–1000):
Use `POST /contacts/batch` (use `batchCreateContacts`):
```json
{
  "campaignId": "<campaignId>",
  "contacts": [
    { "email": "a@example.com", "name": "A", "customFieldValues": [...] },
    { "email": "b@example.com", "name": "B", "customFieldValues": [...] }
  ]
}
```

#### Large batches (>1000 contacts):
1. Check limits: `GET /accounts/sending-limits` (use `getSendingLimits`).
2. Split contacts into chunks of 1000.
3. Send chunks in parallel — up to 10 concurrent requests (respect rate limits: 80 req/s, 30 000 req/10 min).
4. Log any failed chunks and retry once before reporting failure.

> **Rate limit headers**: Every API response includes `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`. If `X-RateLimit-Remaining` drops to 0, wait until `X-RateLimit-Reset` (Unix timestamp) before sending more requests.

### Step 3b — Verify Contact Import (Async)

All contact add endpoints return `202 Accepted` immediately — contacts are processed asynchronously and may appear within seconds or up to several minutes.

> ⚠️ **Ask before starting Step 3 (not after):** determine verification mode upfront so the user can prepare their webhook URL if needed.

**Ask the user which verification mode to use:**

> *"Contacts are added asynchronously. How would you like to verify the import?*
> *A) Webhook (production) — you configure a URL in GetResponse Dashboard → Integrations → Webhooks; provide that URL and the agent will listen for events*
> *B) Webhook (test) — use webhook.site: copy the generated URL to GetResponse Dashboard → Integrations → Webhooks; ⚠️ contact emails pass through an external service — not for production/GDPR*
> *C) Sampling — poll a small contact sample with exponential backoff (no webhook needed, nothing to configure)*
> *You can also specify a custom timeout (default: 10 minutes)."*

---

#### Mode A — Production Webhook

> **Webhook setup in GetResponse (manual — no API available):**
> 1. Log in to GetResponse dashboard.
> 2. Go to **Menu → Integrations & API → API** (or `https://app.getresponse.com/integrations/api`).
> 3. In the **Webhooks** section, click **Add new webhook**.
> 4. Enter the HTTPS URL that will receive events.
> 5. Enable the **Contact subscribed** event.
> 6. Click **Save**.

1. Instruct the user to configure their webhook URL in GetResponse as described above. Ask them to provide that URL to the agent once done.
2. Listen for incoming `subscribe` events on the provided URL — default timeout: **10 minutes** (or as specified by user/agent).
3. Count received events. When expected contact count is reached, or timeout expires → proceed.
4. If timeout reached before all contacts confirmed: report how many were confirmed, continue with Step 4.

---

#### Mode B — Test Webhook (webhook.site)

⚠️ **GDPR warning**: contact email addresses will pass through webhook.site servers (external US service). Only use for development/testing with non-production data. Inform the user before proceeding.

1. Fetch a unique URL: `GET https://webhook.site/token` → save `uuid` and `url`.
2. Provide the generated URL to the user: *"Please paste this URL into GetResponse Dashboard → Integrations → Webhooks: `<webhook.site url>`"*. Wait for the user to confirm they've configured it before continuing.
3. Poll for incoming events: `GET https://webhook.site/token/<uuid>/requests` every **15 seconds**.
   - Count events where `type` = `subscribe`.
   - Stop when expected count reached, or timeout (default: **10 minutes**) expires.
4. Report confirmation count to user, continue with Step 4.

---

#### Mode C — Sampling with Exponential Backoff

Verify a small sample of contacts via `GET /contacts?query[email]=<email>` — do **not** query every contact individually.

**Sample size:**
| Contacts added | Sample size | Max GET requests |
|---|---|---|
| 1–10 | all | ≤ 10 |
| 11–1000 | 5 (first, ~25%, ~50%, ~75%, last) | 5 |
| >1000 (multi-batch) | 1 per batch, max 10 total | ≤ 10 |

**Backoff schedule:**
| Attempt | Wait before check | Elapsed |
|---|---|---|
| 1 | 5 s | 5 s |
| 2 | 15 s | 20 s |
| 3 | 30 s | 50 s |
| 4 | 60 s | ~2 min |
| 5 | 120 s | ~4 min |
| 6 | 300 s | ~9 min |
| 7 (max) | — | timeout |

- If sample is 100% visible → assume full import succeeded, proceed.
- If sample is partially visible → wait and retry.
- After 7 attempts (≈10 min default): report partial confirmation, continue with Step 4.
- Custom timeout: adjust number of attempts proportionally.

---

#### When verification can be skipped entirely

Skip Step 3b if **all** of the following are true:
- Newsletter will be sent to the **whole campaign** (`selectedCampaigns`) — not to individual `selectedContacts`
- User/agent explicitly says verification is not needed

In this case, inform the user: *"Contacts submitted for import (async). Newsletter will be sent to all active contacts in the campaign at send time — no verification needed."*

### Step 4 — Send Newsletter

#### 4a — Get Sender Address
Call `GET /from-fields?query[isDefault]=true` (use `listFromFields`).
Use the `fromFieldId` from the first result. If no default exists, list all and use the first active one.

#### 4b — Determine Recipients
Choose **one** strategy:

| Strategy | When to use | `sendSettings` field |
|---|---|---|
| By campaign | Send to all contacts in the campaign | `selectedCampaigns: ["<campaignId>"]` |
| By custom field | Send to contacts matching a custom field value | Use `searchContactsByConditions` first (see below), then `selectedContacts` |

**Searching by custom field** — call `POST /search-contacts/contacts` (use `searchContactsByConditions`):
```json
{
  "subscribersType": ["subscribed"],
  "sectionLogicOperator": "and",
  "section": [
    {
      "campaignIdsList": ["<campaignId>"],
      "subscriberCycle": ["receiving_autoresponder", "not_receiving_autoresponder"],
      "subscriptionDate": "all_time",
      "logicOperator": "and",
      "conditions": [
        {
          "conditionType": "custom",
          "scope": "<customFieldId>",
          "operator": "is",
          "operatorType": "string_operator_list",
          "value": "<custom_field_value>"
        }
      ]
    }
  ]
}
```
- `campaignIdsList`: array of plain campaignId strings
- `subscriberCycle`: use both values to include all contacts regardless of autoresponder state
- `subscriptionDate`: use `"all_time"` unless filtering by date is needed
- `scope`: the `customFieldId` of the custom field to filter on
- `value`: a plain string (not an array)

Collect the returned `contactId` values, then use `selectedContacts` in the newsletter's `sendSettings`.

#### 4c — Create and Send Newsletter
Call `POST /newsletters` (use `createNewsletter`):
```json
{
  "subject": "<subject line>",
  "name": "<internal name>",
  "type": "broadcast",
  "content": {
    "html": "<FULL HTML CONTENT PROVIDED BY AGENT>",
    "plain": "<plain text version>"
  },
  "fromField": { "fromFieldId": "<id>" },
  "campaign": { "campaignId": "<id>" },
  "sendSettings": {
    "selectedCampaigns": ["<campaignId>"]
  },
  "flags": ["openrate", "clicktrack"]
}
```

- `content.html` must be the complete HTML document provided by the calling agent — do not truncate or modify it.
- Omit `sendOn` to send immediately; include it (ISO 8601) to schedule.
- On success (HTTP 201), report the `newsletterId` and `status` to the user.

---

## Error Handling

| HTTP Code | Meaning | Action |
|---|---|---|
| 202 | Accepted (async) | Normal for contact add — no action needed |
| 400 | Validation error | Read `message` field, fix payload and retry |
| 401 | Invalid API key | Ask user to verify their API key |
| 409 | Already exists | Treat as success for contacts; investigate for others |
| 429 | Rate limit exceeded | Read `Retry-After` header (seconds). Inform the user: *"Rate limit reached — pausing for Ns and resuming."* Sleep that duration, then retry the failed request. |
| 500 | Server error | Retry once after 5 seconds; report if persists |

---

## Rate Limits Reference

- **Per second**: max **80 requests/second** per API key
- **Per 10-minute window**: max **30,000 requests** (reset every 10 minutes)
- **Parallel requests**: max **10 concurrent** requests
- **Batch import**: max 1000 contacts per `/contacts/batch` call
- **Newsletter sending**: subject to account plan limits (check via `getSendingLimits`)
- Always read `X-RateLimit-Remaining` from response headers; if 0, pause before the next call
- On HTTP 429: read `Retry-After` header (value in seconds, typically 1), inform the user about the pause, sleep that duration, then retry the request
- Response headers on 429: `Retry-After: <s>`, `X-RateLimit-Limit: 80`, `X-RateLimit-Remaining: 0`, `X-RateLimit-Reset: <s> seconds`
- For large parallel operations (>10 concurrent), spread requests in waves of 10 to avoid hitting 80 req/s

---

## Key Rules

- Always check if a campaign or custom field exists before creating it — avoid duplicates.
- Custom field `name` must be lowercase with underscores (e.g. `company_name`, not `Company Name`).
- Custom field `value` in contact payloads is always an **array**: `["value"]`, never a plain string.
- The HTML newsletter content is defined by the calling agent — never generate placeholder HTML.
- Never expose or log the API key in outputs.
- If any required piece of information is missing (API key, campaign name, HTML content), ask the user before proceeding.
