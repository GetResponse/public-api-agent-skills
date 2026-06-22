# Usage Examples

## Example 1: Add contacts with custom fields and send newsletter to campaign

**User prompt:**
> Add these contacts to my "Q2-Leads" campaign. Each has a "department" field. Then send them an HTML newsletter with subject "Welcome to Q2".

**Agent execution flow:**

### Step 1 — Resolve campaign
```
GET /campaigns?query[name]=Q2-Leads
→ Not found
POST /campaigns  { "name": "Q2-Leads", "optinTypes": { "api": "single" } }
→ { "campaignId": "camp_abc123" }
```

### Step 2 — Resolve custom field "department"
```
GET /custom-fields?query[name]=department
→ Not found
POST /custom-fields  { "name": "department", "type": "text" }
→ { "customFieldId": "cf_dept456" }
```

### Step 3 — Batch import contacts
```
POST /contacts/batch
{
  "campaignId": "camp_abc123",
  "contacts": [
    { "email": "alice@corp.com", "name": "Alice", "customFieldValues": [{ "customFieldId": "cf_dept456", "value": ["Engineering"] }] },
    { "email": "bob@corp.com",   "name": "Bob",   "customFieldValues": [{ "customFieldId": "cf_dept456", "value": ["Sales"] }] }
  ]
}
→ 202 Accepted
```

### Step 4a — Get sender address
```
GET /from-fields?query[isDefault]=true
→ [{ "fromFieldId": "ff_xyz789", "email": "sender@mycompany.com" }]
```

### Step 4c — Send newsletter
```
POST /newsletters
{
  "subject": "Welcome to Q2",
  "name": "Q2-Welcome-Newsletter",
  "type": "broadcast",
  "content": {
    "html": "<!DOCTYPE html><html><body><h1>Welcome!</h1><p>We are excited to have you.</p></body></html>",
    "plain": "Welcome! We are excited to have you."
  },
  "fromField": { "fromFieldId": "ff_xyz789" },
  "sendSettings": {
    "selectedCampaigns": [{ "campaignId": "camp_abc123" }]
  },
  "flags": ["openrate", "clicktrack"]
}
→ 201 { "newsletterId": "nl_def101", "status": "scheduled" }
```

---

## Example 2: Send newsletter only to contacts where department = "Engineering"

**User prompt:**
> Send a newsletter to all contacts in the "Engineering" department. HTML content: `<h1>Tech Update</h1><p>See what's new.</p>`

### Step 4b — Search contacts by custom field
```
POST /search-contacts/contacts?perPage=1000
{
  "subscribersType": ["subscribed"],
  "sectionLogicOperator": "and",
  "section": [
    {
      "logicOperator": "and",
      "conditions": [
        {
          "conditionType": "custom_field",
          "operator": "is",
          "operatorType": "string",
          "value": ["Engineering"]
        }
      ]
    }
  ]
}
→ [{ "contactId": "c_001" }, { "contactId": "c_002" }]
```

### Step 4c — Send newsletter to specific contacts
```
POST /newsletters
{
  "subject": "Tech Update — Engineering Team",
  "name": "tech-update-eng",
  "type": "broadcast",
  "content": {
    "html": "<h1>Tech Update</h1><p>See what's new.</p>",
    "plain": "Tech Update — See what's new."
  },
  "fromField": { "fromFieldId": "ff_xyz789" },
  "sendSettings": {
    "selectedContacts": [
      { "contactId": "c_001" },
      { "contactId": "c_002" }
    ]
  }
}
→ 201 { "newsletterId": "nl_ghi202", "status": "scheduled" }
```

---

## Example 3: Large batch (2500 contacts)

**Agent execution flow:**

1. Check limits: `GET /accounts/sending-limits`
2. Split into 3 chunks: [1000, 1000, 500]
3. Send chunks 1 & 2 & 3 in parallel (3 concurrent requests):
   ```
   POST /contacts/batch  { "campaignId": "...", "contacts": [...1000 contacts...] }
   POST /contacts/batch  { "campaignId": "...", "contacts": [...1000 contacts...] }
   POST /contacts/batch  { "campaignId": "...", "contacts": [...500 contacts...] }
   ```
4. Monitor `X-RateLimit-Remaining` header; if it reaches 0 in any response, pause all further calls until `X-RateLimit-Reset`
5. Retry any failed chunk once before reporting error

---

## Example 4: Scheduled newsletter

```
POST /newsletters
{
  "subject": "Monthly Newsletter — June",
  "name": "monthly-june",
  "type": "broadcast",
  "content": { "html": "...", "plain": "..." },
  "fromField": { "fromFieldId": "ff_xyz789" },
  "sendSettings": { "selectedCampaigns": [{ "campaignId": "camp_abc123" }] },
  "sendOn": "2026-06-01T09:00:00+02:00"
}
```
`sendOn` accepts ISO 8601 with timezone offset.
