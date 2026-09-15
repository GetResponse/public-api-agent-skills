# Contact imports

## Choose an operation

| Need | Endpoint | Acceptance |
|---|---|---|
| Add one contact | `POST /contacts` | `202`, no job ID |
| Add 2–1000 contacts | `POST /contacts/batch` | `202`, no job ID |
| Add/update rows with trackable statistics | `POST /imports` | `201`, retain `importId` |

Resolve the campaign and requested field/tag definitions first. State how existing contacts will
be handled (skip, update selected values, or tracked import). Never convert an add-only request
into an updating import without that choice. Preflight duplicate emails within the input and
destination list; identical input rows can be collapsed with a reported count, conflicting rows
need resolution. Keep literal `+` aliases intact. Use a scoped scan for large inputs.

Do not change list opt-in settings to make verification easier. Adding contacts may produce
confirmation mail under the list's existing settings. Omit cycle enrollment unless requested;
check existing automation effects when relevant. Do not re-add deleted/blocked contacts as
automatic error recovery.

## Payloads

Single contact (IDs in nested objects):

```json
{"email":"anna@example.com","campaign":{"campaignId":"listA"},"tags":[{"tagId":"tagA"}],"customFieldValues":[{"customFieldId":"fieldA","value":["gold"]}]}
```

Batch uses a top-level campaign ID and a DIFFERENT tag shape:

```json
{"campaignId":"listA","contacts":[{"email":"anna@example.com","tags":{"ids":["tagA"]}},{"email":"jan@example.com"}]}
```

Tracked import uses names and row arrays, not contact payload objects:

```json
{"campaignId":"listA","fieldMapping":["email","name","customer_tier","tag:vip_customer"],"contacts":[["anna@example.com","Anna","gold","1"],["jan@example.com","Jan","silver","0"]]}
```

Every row must align with fieldMapping and include email. Resolve custom field names/types and
use strings in rows per the bundled schema. `ip` is the import mapping name; single/batch uses
`ipAddress`. Tag `"1"` attaches; `"0"` does not attach and DOES NOT detach an existing tag.
Import supports only a single value per custom field. For multi-value fields use the contact
endpoints; never truncate an array to make an import fit. Do not map consent or arbitrary cycle
settings as custom fields. Although imports can create tag names, create requested tags explicitly
after GET-first so misspellings do not silently become definitions.

CSV/TSV is local input, never sent as CSV to these JSON endpoints. Parse using a CSV library,
preserve quoted delimiters/Unicode, validate headers and row widths, and agree blank-cell behavior
before updates. Omitted and empty field values are not interchangeable; reject ambiguous rows
or split them into explicit contact updates. Do not download input or send contact data to an
external conversion/webhook service without the user's authorization.

## Limits

The official batch contract specifies 1000 contacts/request, 1 call/second and 80 calls/10 minutes.
Split larger add-only inputs into chunks with those limits; do not copy the older parallelism
assumptions from other skill packages. Default to sequential requests, pace submissions, and
honor returned throttling headers.

Tracked imports allow a 20 MB request, one active import per campaign, two active imports per
account and 20 imports/24 hours. Keep JSON under 20,000,000 UTF-8 bytes as a conservative local
cap. Active states: `uploaded`, `to_review`, `review`, `approved`. Check paginated `/imports`
before submission and account for other processes. `409` is a conflict, not completion.
Do not fabricate an available daily quota from a partially scanned history.

Sources: [batch guide](https://apidocs.getresponse.com/v3/case-study/adding-batch-contacts),
[import guide](https://apidocs.getresponse.com/v3/case-study/create-import).
The prose import guide sometimes says `/import`; the actual OpenAPI paths are plural `/imports`.

## Verify single/batch acceptance

Set a deadline of 10 minutes and at most 30 verification GETs per task. For 1–5 records check all;
for larger submissions choose five representative emails across chunks. Check only pending
sample members after waits of 5, 15, 30, 60, 120 and 300 seconds, constrained by the deadline.
Each email lookup is scoped to campaign and exact match; verify requested values, not just
existence. An existing record is not evidence that a submitted update took effect.

A sample cannot prove a whole batch succeeded. Report submitted/accepted counts separately from
verified sample counts. Unconfirmed double-opt-in contacts may not appear in active `/contacts`;
at timeout report unresolved/pending rather than rejection or success. Never resubmit because
polling expired. An already configured, observable subscribe webhook can supplement the evidence;
deduplicate events and correlate email/list/time. Do not create webhook infrastructure by default.

## Verify tracked imports

Save `importId` immediately. Poll `GET /imports/{importId}` with the same six waits and deadline.
`finished` is terminal, but inspect `statistics` and `errorStatistics`: uploaded, invalid, updated,
addedToList, and rejection categories. Live testing found that the first `finished` result may
precede complete statistics. Within the existing deadline, wait until uploaded matches the input
row count and invalid + updated + addedToList accounts for those rows. If accounting remains
incomplete, report finished with unverified statistics, not failure or full success; preserve the
job ID and do not resubmit. A finished job with invalid rows is a partial result.
`rejected` and `canceled` are terminal failures; other states remain pending, even after timeout.
Report the job ID for later continuation. An observable existing import-finished webhook is an
alternative trigger to read final job details.

After a submission timeout without an ID, inspect recent campaign imports and reconcile the
candidate job using available evidence. If multiple/uncertain candidates remain, report unknown
acceptance and do not submit again. Never assume an undocumented idempotency key prevents duplicates.
