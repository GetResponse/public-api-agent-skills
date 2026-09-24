# Search Contacts API guide

## Source and verification status

This skill covers the `Search Contacts` API tag in the official
[OpenAPI reference](https://apireference.getresponse.com/open-api.json), inspected on 2026-09-22,
and the official [Segments (search contacts) manual](https://apidocs.getresponse.com/v3/case-study/segments-manual).
The published specification reports version `3.2026-08-20T11:07:16+00:00`.

An SMB live run on the user-authorized `grapi2` account was recorded on 2026-09-22 in the repository
at `tests/getresponse-search-contacts-skill/LIVE_RESULTS.md`. It confirmed all eight skill endpoints,
core condition grammar and saved-segment lifecycle. The bulk custom-field request was intentionally
run against a verified zero-match segment, so its `202` acceptance is live verified but its effect on
a real contact is not. Feature-specific condition variants remain documentation-derived. The local
`openapi.json` is a deliberately small operation contract, not a replacement for the condition manual.

## Connection and pagination

Base URL: `https://api.getresponse.com/v3`. Authenticate with
`X-Auth-Token: api-key <key>` or OAuth `Authorization: Bearer <token>`. GetResponse MAX needs the
account's confirmed endpoint plus `X-Domain`; never infer a domain or region. Send
`X-Request-Source: getresponse/getresponse-search-contacts-skill@1.0.0` and
`Content-Type: application/json` for POSTs.

List/search result endpoints use `page` (starting at 1) and `perPage` (1–1000; default 100).
Use `TotalCount`, `TotalPages`, and `CurrentPage` when returned. Stop at an empty page. A failed or
user-capped traversal is not proof that no more contacts match. Use `perPage=1` only for a count
preview, not as a substitute for returning requested results.

## Supported operations and risk

| Operation | Purpose | Risk / required handling |
|---|---|---|
| `POST /search-contacts/contacts` | Run an advanced, unsaved query | Medium: potentially broad read; scope conditions, paginate and report result count |
| `GET /search-contacts` | List saved segments | Low: name/date query only, exact-match the chosen name locally |
| `POST /search-contacts` | Create saved segment | Medium: durable resource; list first and create only if requested |
| `GET /search-contacts/{id}` | Read a segment definition | Low: use before update/delete/bulk write |
| `POST /search-contacts/{id}` | Replace a saved segment definition | Medium: preview existing definition and ask on name/intent ambiguity |
| `DELETE /search-contacts/{id}` | Delete saved segment | High: exact ID and explicit authorization; verify `404` on a follow-up GET when appropriate |
| `GET /search-contacts/{id}/contacts` | List contacts matched by segment | Medium: broad read; paginate and bound output |
| `POST /search-contacts/{id}/custom-fields` | Upsert fields for every matching contact | High and asynchronous (`202`): preview count + exact values + explicit authorization, then bounded sample verification |

## Errors and retry policy

| Response | Action |
|---|---|
| `400` | Inspect the documented condition/operator dependency; correct only a known user input, never substitute another condition |
| `401` / `403` | Stop and resolve credentials/access; do not retry |
| `404` | Re-resolve the segment ID; do not recreate it automatically |
| `409` | Read the conflicting saved segment and report it; a name conflict is not approval to update it |
| `429` | Honor `Retry-After`, else `X-RateLimit-Reset`; retry safe reads at most twice |
| timeout / `5xx` | Retry safe reads at most twice with backoff; reconcile persistent writes before considering another attempt |

`202 Accepted` from the segment-wide custom-field upsert means the request entered processing; it
does not prove that all matches changed. Poll only a small, known sample on a bounded schedule and
report the operation as unverified if it has not converged by the agreed deadline. Never resend an
uncertain bulk write.

The global documentation currently gives a 10-minute quota window, 30,000 calls per window,
80 calls per second, and 10 simultaneous requests. Treat endpoint-specific server headers as
authoritative and do not load-test an account.

## Boundaries with the contacts skill

`GET /contacts` supports only simple query fields such as email, name, campaign, origin and dates.
It does not support tag/custom-field filters. Search Contacts owns the advanced query grammar and
saved-filter lifecycle; Contacts owns the individual contact records. A workflow may use both only
when each action is independently in scope.
