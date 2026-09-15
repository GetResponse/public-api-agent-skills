# Worked examples

These are illustrative flows with symbolic IDs, not records of live API runs.
Use the authentication headers from the API guide for every request.

## 1. Update one contact without dropping tags

User: “Zmień imię Anny anna@example.com na liście Klienci na Anna Kowalska.”

1. `GET /campaigns?query[name]=Klienci`, exact match → `listA`.
2. `GET /contacts?query[email]=anna@example.com&query[campaignId]=listA&additionalFlags=exactMatch`
   → one contact, `contactA`. Query examples are decoded for readability; encode on the wire.
3. `GET /contacts/contactA` → current data, including existing tags/fields.
4. `POST /contacts/contactA` with `{"name":"Anna Kowalska"}` → `200`.
5. Detail GET → name verified. Report the change; tag and field collections were not sent.

## 2. Detach one tag and one field

User: “Usuń tag trial i pole trial_end u contactA. Zachowaj pozostałe dane.”

Resolve `trial` → `tagA`, `trial_end` → `fieldA`, verify contactA and its list. Fresh detail
contains tags A/B and fields A/B, with B holding two values. Build a replacement using the helper:

```json
{"tags":[{"tagId":"tagB"}],"customFieldValues":[{"customFieldId":"fieldB","value":["one","two"]}]}
```

POST to `/contacts/contactA` → `200`. Re-read: A assignments absent, B and both its values retained.
Do not call `DELETE /tags/tagA` or delete the field definition. If a fresh read lacks a complete
affected collection, stop rather than sending an empty replacement.

## 3. Import a CSV with updates and statistics

User: “Zaimportuj ten CSV do Klientów i aktualizuj imię istniejących kontaktów.”

Parse CSV locally; validate email/name columns, row widths and duplicate emails. Resolve listA.
GET `/imports` with pagination → capacity available. Submit:

```text
POST /imports
{"campaignId":"listA","fieldMapping":["email","name"],"contacts":[["anna@example.com","Anna"],["jan@example.com","Jan"]]}
```

`201` returns importA with `uploaded` status. Poll `/imports/importA` within the bounded schedule.
If finished statistics show uploaded=2, updated=1, addedToList=0, invalid=1, report a partial
result with the returned error categories. Do not say both contacts were imported; do not resend
the entire job. If the job remains in review, report its ID and pending state.

## 4. Move or delete the correct membership

User: “Przenieś anna@example.com z Trial do Klienci.”

Resolve both lists and the source contact. If destination lookup finds another membership,
explain the conflict and ask which outcome is intended; do not merge/delete as a workaround.
Otherwise preview the exact move under the existing request, POST only the destination campaign
object, and GET the contact to verify its new list.

For “Usuń contactA z listy Trial” verify that ID actually belongs to Trial first. If the target
matches the authorized request, DELETE → `204`, then GET → `404`. Report that membership removed,
not global erasure or a future-subscription block.

## 5. Consent lookup and scope boundaries

User: “Pokaż zgody marketingowe contactA i daty ich zmian.”

Resolve the contact; GET `/contacts/contactA/consents` → grants/content/history. Report returned
state and timestamps, optionally resolving `/gdpr-fields/{gdprFieldId}` for a definition.
No records returned is not a positive grant. Do not write a custom field to simulate consent.

For “Utwórz zapisany segment VIP i wyślij newsletter”, explain that segment management and sending
belong to separate skills. This contact skill neither creates `/search-contacts` nor sends mail.
