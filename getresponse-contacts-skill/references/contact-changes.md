# Contact changes

## Update only the requested properties

Read `GET /contacts/{contactId}`. Build a writable payload, not a copy of the response:

```json
{"name":"Anna Kowalska","note":"Requested callback"}
```

`POST /contacts/{contactId}` returns `200`. Re-read and verify requested fields. Leave unrelated
properties out. `scoring: null` clears the score; `dayOfCycle: null` removes the contact from
the autoresponder cycle. Do not send either without a corresponding request. An email change
requires an exact target and conflict checks within its list; never silently combine contacts.

## Add tags and upsert field values

Resolve definition IDs using the API guide. Dedicated endpoints preserve unrelated assignments:

```text
POST /contacts/{contactId}/tags
{"tags":[{"tagId":"tagA"}]}

POST /contacts/{contactId}/custom-fields
{"customFieldValues":[{"customFieldId":"fieldA","value":["gold"]}]}
```

Both return `200`. Upsert does not detach tags or fields. A field upsert updates that field's
value collection: to add one option to a multi-value field, first read and merge its existing
values. Verify both the intended values and preservation of unrelated assignments.

## Remove assignments without losing other data

General update replaces any supplied `tags` or `customFieldValues` collection. To detach:

1. Read a fresh, complete contact detail (no `fields` projection).
2. Remove only the requested IDs; retain remaining tag IDs and all remaining field values.
3. Send only the affected collection to `POST /contacts/{contactId}`. An empty array means
   clear that collection and is valid only when all assignments in it were targeted.
4. Re-read and check removed IDs are absent and retained values remain unchanged.

Use the offline helper to build the replacement from a fresh detail snapshot:

```bash
python3 scripts/contact_payloads.py remove-tags --ids tagA < contact.json > update.json
python3 scripts/contact_payloads.py remove-fields --ids fieldA < contact.json > update.json
```

Paths are relative to the installed skill. The helper never calls the API. Its input must contain
the complete affected collection; it fails on absent/ambiguous data. Empty output `{}` means
the requested IDs are already absent, so skip the write. Protect/remove local contact snapshots
according to the user's data handling requirements; do not commit them.

There is no conditional-write guarantee documented for these operations. Keep read and write
close together. If concurrent updates are observed, stop and report rather than repeating a
replacement that could lose another writer's changes.

## Move to another list

Resolve source contact and destination campaign. Search for the same email in the destination
before the write. If already present, stop and ask how to handle the two memberships; do not
delete or merge either as conflict recovery. If the contact is already in the desired list,
report no change.

Send `{"campaign":{"campaignId":"destinationId"}}` to `POST /contacts/{contactId}`.
This is a move, with history and statistics transferred, not a copy. Preview source, destination,
email, and relevant subscription/automation effects. Re-read the contact and verify its campaign.
Do not change `dayOfCycle` incidentally; resolve intended cycle behavior if material to the move.

## Delete a contact

Distinguish removing a membership, simulating an unsubscribe, and blocking future subscription.
This version supports removal of an exact contact using `DELETE /contacts/{contactId}`.
Do not claim permanent erasure from all GetResponse data or removal from every list.

Preview email, list and ID and use the user's existing authorization if it covers that exact
deletion. A broad/ambiguous cleanup request needs concrete targets first. Snapshot the authorized
target IDs before a bulk delete; do not paginate a shrinking list while deleting it.
Expect `204`, then verify `GET /contacts/{contactId}` returns `404`. If already missing, report
already absent, not newly deleted. Never add `messageId` implicitly: it simulates an unsubscribe
from a message and changes the meaning of the operation. Explicit message-based unsubscribe
and blocklist management are outside this version.

## Read consent evidence

`GET /contacts/{contactId}/consents` returns consent IDs, content, `isGranted`, and history.
Use `GET /gdpr-fields` or `GET /gdpr-fields/{gdprFieldId}` for definitions when needed. Report
returned state and timestamps verbatim in meaning; an empty collection means no consent records
were returned. Do not infer a grant, legal basis, or permission to send from list membership,
custom fields, a tag, or a successful import. No consent-writing endpoint is included.
