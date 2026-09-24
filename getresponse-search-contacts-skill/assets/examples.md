# Examples

## One-off search: subscribed contacts tagged VIP who have not opened a message

Resolve the tag and message IDs first. Then run `POST /search-contacts/contacts` with the saved
condition grammar, paginate, and report the `TotalCount` before returning contact details.

```json
{
  "subscribersType": ["subscribed"],
  "sectionLogicOperator": "and",
  "section": [{
    "campaignIdsList": ["campaign-id"],
    "logicOperator": "and",
    "subscriberCycle": ["receiving_autoresponder", "not_receiving_autoresponder"],
    "subscriptionDate": "all_time",
    "conditions": [
      {"conditionType": "tag", "operatorType": "exists", "operator": "exists", "value": "vip-tag-id"},
      {"conditionType": "not_opened", "operatorType": "message_operator", "operator": "newsletter", "value": "message-id"}
    ]
  }]
}
```

## Saved segment: consent and custom field

For “save a segment named EU consented customers”, first resolve the GDPR field and custom-field
IDs, list existing saved segments by name, then `POST /search-contacts` only if creation was
requested and there is no ambiguity. Use the same condition envelope plus `name`. Saved segments
target subscribed contacts; do not copy a one-off `unconfirmed` audience into one.

## Update a saved segment

GET `/search-contacts/{id}` first and show the existing criteria. Replace the full definition with
`POST /search-contacts/{id}` only after the user confirms the revised logical grouping; updating
one condition is not a patch operation.

## Bulk custom field upsert

For “mark every contact in segment X as renewal_candidate”, GET segment X and GET
`/search-contacts/{id}/contacts?perPage=1` to obtain a count. Present the exact field ID/value and
that all current matches will change. After explicit approval, POST:

```json
{"customFieldValues": [{"customFieldId": "renewal-field-id", "value": ["true"]}]}
```

The `202` response is only acceptance. Poll a bounded sample from the segment to verify the
expected value; do not replay an uncertain upsert. This upsert does not authorize adding/removing
tags, moving, deleting, exporting, or messaging the matched contacts.
