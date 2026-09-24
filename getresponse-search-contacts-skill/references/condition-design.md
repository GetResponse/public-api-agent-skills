# Condition design

Read the [official segments manual](https://apidocs.getresponse.com/v3/case-study/segments-manual)
before constructing a condition other than a simple name or email comparison. It defines the
condition-specific required fields, operator/value dependencies, and resource IDs.

## Envelope and grouping

An ad-hoc request requires `subscribersType`, `sectionLogicOperator`, and `section`. A saved
segment additionally needs a unique `name`; its subscriber type is subscribed contacts.

`sectionLogicOperator` joins sections. Each section has its own `logicOperator`, campaign scope,
autoresponder-cycle scope, subscription date period and up to eight `conditions`. The manual allows
up to eight sections. In natural language, preserve parentheses: “A and (B or C)” needs distinct
groups; do not turn it into “A and B or C”.

```json
{
  "subscribersType": ["subscribed"],
  "sectionLogicOperator": "and",
  "section": [{
    "campaignIdsList": ["campaign-id"],
    "logicOperator": "and",
    "subscriberCycle": ["receiving_autoresponder", "not_receiving_autoresponder"],
    "subscriptionDate": "all_time",
    "conditions": [{
      "conditionType": "tag",
      "operatorType": "exists",
      "operator": "exists",
      "value": "tag-id"
    }]
  }]
}
```

## Available condition families

The API currently enumerates: `name`, `email`, `custom`, `subscription_date`,
`subscription_method`, `opened`, `not_opened`, `phase`, `last_send_date`, `last_click_date`,
`last_open_date`, `webinar`, `clicked`, `not_clicked`, `sent`, `not_sent`, `geo`, `gdpr`, `score`,
`engagement_score`, `tag`, `goal`, `crm`, `ecommerce_number_of_purchases`,
`ecommerce_total_spent`, `ecommerce_product_purchased`, `ecommerce_brand_purchased`,
`ecommerce_abandoned_cart`, `sms_sent`, `sms_link_clicked`, `sms_link_not_clicked`, and
`custom_event`.

Many types need IDs that belong to another product domain: custom-field, tag, GDPR field, message,
webinar, goal, CRM pipeline/stage, shop, product/brand, SMS, click-track, or custom event. Resolve
them with the corresponding documented read endpoint, or ask for the verified ID. Do not select the
first fuzzy name match and do not create external resources merely to make a filter work.

## Operator dependencies

- Name/email use `string_operator`; valid operators include `is`, `is_not`, `contains`,
  `not_contains`, `starts`, `ends`, `not_starts`, and `not_ends`.
- Custom-field operators depend on the field definition: list/string, numeric and date conditions
  take different operator/value shapes. Read the manual section for that field type.
- Date/activity conditions often accept a relative period or a specific date/range. Include the
  extra value only when that selected operator requires it.
- Conditions such as tag presence or assigned/not-assigned fields encode existence in the operator;
  do not supply a comparison value where the manual prohibits one.

For any unsupported combination, tell the user which exact detail is needed rather than guessing.
