# Examples

## Create a welcome message safely

User: “Create a welcome autoresponder for my `Trial leads` list, but don't activate it yet.”

1. Search campaigns by name and confirm the exact match. If it does not exist, ask whether to
   create `Trial leads`; after confirmation, create the list and retain its returned `campaignId`.
   List approved from-fields if the sender was not supplied.
2. Search `GET /autoresponders?query[name]=Welcome — day 0` to avoid a duplicate.
3. Create with `status: disabled`, explicit sender, the supplied content, `sendSettings.type:
   signup`, and `triggerSettings.dayOfCycle: 0`.
4. Fetch the returned ID and report the verified configuration. Do not enable it.

## Create a list and import its initial recipients

User: “Create the `Trial leads` list and import these 240 contacts before preparing a welcome
autoresponder.”

1. Confirm that creating the named list is intended, then create it and keep its `campaignId`.
2. Validate the supplied contacts and import them in one batch of 240.
3. Sample a few imported email addresses with bounded backoff because the `202` response is
   asynchronous. Report the accepted and verified results before creating the disabled message.

## Verify an import with a production webhook

User: “Import these contacts and verify the result through our webhook.”

1. Ask for the observable HTTPS endpoint and have the user configure it manually in GetResponse
   with the **Contact subscribed** event.
2. Confirm that the agent can read the resulting event log or queue. If it cannot, choose sampling.
3. Submit the import only after the verification mode is selected. Count matching `subscribe`
   callbacks until all expected contacts are confirmed or the timeout expires, then report the
   precise confirmation count.

## Activate an existing message

User: “Turn on Welcome — day 0 for Trial leads.”

1. Resolve the exact autoresponder and fetch its details.
2. State its ID, campaign, sender, subject, and trigger; ask for confirmation immediately before
   enabling.
3. After confirmation, update status to `enabled`, fetch it again, and report the result.

## Report performance

User: “How is our onboarding autoresponder doing?”

Resolve the exact message, request its statistics, and report returned delivery/open/click measures
with the API's stated range. Do not infer causality or change the message.

## Refuse action-based automation

User: “Send an email whenever a customer buys product X.”

Explain that this is an action-based marketing-automation workflow, which this autoresponder skill
does not manage; do not attempt to represent it as a time-based autoresponder.
