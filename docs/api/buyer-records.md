# Buyer Records

Buyer Records store pre-contract buyer information. Starting October 12, 2026,
create buyer transactions from a Buyer Record instead of posting directly to
`transaction-builder`. Direct listing creation remains supported. Dual-sided
transactions require both Buyer Record and listing associations.

The contract below follows [Real's migration guidance](https://support.therealbrokerage.com/hc/en-us/articles/43709711732887-Buyer-Record-API-Change-Guidance)
and the [public Arrakis Swagger](https://arrakis.therealbrokerage.com/swagger-ui/index.html),
verified October 2, 2026.

## Create and convert

Use the actual buyer brokerage agreement dates and the agent's authorized office.
Do not infer agreement dates from a purchase contract. The creation fields
`officeId`, `geographicInterest`, `bbaDates`, and `initialParticipants` are required.
External participant email uses `emailAddress`; participant creation uses `role`.

```python
from rezen import RezenClient

client = RezenClient()  # Reads REZEN_API_KEY.
buyer_record = client.buyer_records.create_buyer_record({
    "officeId": "00000000-0000-0000-0000-000000000001",
    "geographicInterest": "Salt Lake County",
    "bbaDates": {"start": "2026-10-01", "end": "2026-12-31"},
    "initialParticipants": [{
        "externalParticipant": {
            "firstName": "Test",
            "lastName": "Buyer",
            "emailAddress": "buyer@example.com",
            "externalParticipantType": "PERSON",
            "role": "BUYER",
        }
    }],
})
# Persist the record ID before conversion so a retry can resume this record.
buyer_record_id = buyer_record["id"]
builder = client.buyer_records.build_transaction(buyer_record_id)
builder_id = builder["id"]
# Continue populating the returned builder with the existing builder methods.
```

Replace illustrative IDs, agreement dates, and participant details with real
authorized data. Optional creation fields include `teamId` and `createOnBehalfOf`.
Conversion accepts no request body and returns a Transaction Builder object.
Conversion is a write: persist its returned builder ID before later steps and
reconcile an uncertain response before retrying; the SDK does not promise
idempotency for repeated conversion calls.

For a dual-sided transaction, associate the existing listing before submission:

```python
client.transaction_builder.update_associations(builder_id, {
    "buyerRecordId": buyer_record_id,
    "listingId": "00000000-0000-0000-0000-000000000002",
})
```

## Endpoint reference

All methods use the Arrakis `/api/v1` base and the client's normal authentication,
timeout, retry, and error handling. Request dictionaries preserve native camelCase
fields. Successful `204` responses return `{}`.

| Method | HTTP route | Request |
| --- | --- | --- |
| `create_buyer_record(data)` | `POST /buyer-record` | Creation fields above |
| `search_buyer_records(params=None)` | `GET /buyer-record` | Native query filters |
| `get_buyer_record(id)` | `GET /buyer-record/{id}` | None |
| `update_buyer_record(id, data)` | `PATCH /buyer-record/{id}` | Fields to change |
| `add_participant(id, data)` | `POST /buyer-record/{id}/participant` | `internalParticipant` or `externalParticipant` |
| `update_participant(id, participant_id, data)` | `PATCH /buyer-record/{id}/participant/{participant_id}` | Wrapper with update fields; role is `participantRole` |
| `delete_participant(id, participant_id)` | `DELETE /buyer-record/{id}/participant/{participant_id}` | None |
| `build_transaction(id)` | `POST /buyer-record/{id}/build-transaction` | None |
| `request_termination(id, reason)` | `PATCH /buyer-record/{id}/request-termination` | `reason` (max 255 characters) |
| `cancel_termination_request(id)` | `PATCH /buyer-record/{id}/cancel-termination-request` | None |

Search supports `pageNumber`, `pageSize`, `sortBy`, `sortDirection`, `ownerIds`,
`officeIds`, `teamIds`, `lifecycleStates`, `searchText`, and date filters. It returns
`buyerRecords`, `pageNumber`, `pageSize`, `hasNext`, and `totalCount`.

```python
page = client.buyer_records.search_buyer_records({
    "pageNumber": 0,
    "pageSize": 25,
    "lifecycleStates": ["ACTIVE"],
    "sortDirection": "DESC",
})
```

::: rezen.buyer_records.BuyerRecordsClient

## Related topics

- [Transaction Builder](transaction-builder.md)
- [Transaction workflows](../guides/transactions.md)
