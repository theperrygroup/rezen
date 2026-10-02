"""HTTP contract tests for the October 2026 Buyer Record workflow."""

import json
from typing import Any, Tuple
from urllib.parse import parse_qs, urlparse

import pytest
import responses

from rezen import BuyerRecordsClient, RezenClient
from rezen.exceptions import ValidationError

BASE_URL = "https://arrakis.therealbrokerage.com/api/v1"
RECORD_ID = "00000000-0000-0000-0000-000000000001"
PARTICIPANT_ID = "00000000-0000-0000-0000-000000000002"
CREATE_DATA = {
    "officeId": "00000000-0000-0000-0000-000000000003",
    "geographicInterest": "Salt Lake County",
    "bbaDates": {"start": "2026-10-01", "end": "2026-12-31"},
    "initialParticipants": [
        {
            "externalParticipant": {
                "firstName": "Test",
                "lastName": "Buyer",
                "emailAddress": "buyer@example.com",
                "externalParticipantType": "PERSON",
                "role": "BUYER",
            }
        }
    ],
}


@pytest.mark.parametrize(
    "method,args,http_method,path,payload,status,response_data",
    [
        (
            "create_buyer_record",
            (CREATE_DATA,),
            "POST",
            "",
            CREATE_DATA,
            201,
            {"id": RECORD_ID},
        ),
        (
            "get_buyer_record",
            (RECORD_ID,),
            "GET",
            f"/{RECORD_ID}",
            None,
            200,
            {"id": RECORD_ID},
        ),
        (
            "update_buyer_record",
            (RECORD_ID, {"geographicInterest": "Utah County"}),
            "PATCH",
            f"/{RECORD_ID}",
            {"geographicInterest": "Utah County"},
            204,
            None,
        ),
        (
            "add_participant",
            (
                RECORD_ID,
                {
                    "internalParticipant": {
                        "userId": PARTICIPANT_ID,
                        "role": "BUYERS_AGENT",
                    }
                },
            ),
            "POST",
            f"/{RECORD_ID}/participant",
            {"internalParticipant": {"userId": PARTICIPANT_ID, "role": "BUYERS_AGENT"}},
            201,
            {"id": RECORD_ID},
        ),
        (
            "update_participant",
            (
                RECORD_ID,
                PARTICIPANT_ID,
                {"internalParticipant": {"participantRole": "TEAM_LEADER"}},
            ),
            "PATCH",
            f"/{RECORD_ID}/participant/{PARTICIPANT_ID}",
            {"internalParticipant": {"participantRole": "TEAM_LEADER"}},
            204,
            None,
        ),
        (
            "delete_participant",
            (RECORD_ID, PARTICIPANT_ID),
            "DELETE",
            f"/{RECORD_ID}/participant/{PARTICIPANT_ID}",
            None,
            204,
            None,
        ),
        (
            "build_transaction",
            (RECORD_ID,),
            "POST",
            f"/{RECORD_ID}/build-transaction",
            None,
            200,
            {"id": "builder-id", "buyerRecordId": RECORD_ID},
        ),
        (
            "request_termination",
            (RECORD_ID, "Buyer cancelled"),
            "PATCH",
            f"/{RECORD_ID}/request-termination",
            {"reason": "Buyer cancelled"},
            204,
            None,
        ),
        (
            "cancel_termination_request",
            (RECORD_ID,),
            "PATCH",
            f"/{RECORD_ID}/cancel-termination-request",
            None,
            204,
            None,
        ),
    ],
)
@responses.activate
def test_buyer_record_http_contract(
    method: str,
    args: Tuple[Any, ...],
    http_method: str,
    path: str,
    payload: Any,
    status: int,
    response_data: Any,
) -> None:
    """Verify each endpoint's verb, request body, and no-content handling."""
    responses.add(
        http_method, f"{BASE_URL}/buyer-record{path}", json=response_data, status=status
    )
    result = getattr(BuyerRecordsClient(api_key="test-key"), method)(*args)
    assert result == (response_data or {})
    request = responses.calls[0].request
    assert request.headers["X-API-KEY"] == "test-key"
    assert (json.loads(request.body) if request.body else None) == payload


@pytest.mark.parametrize(
    "params",
    [
        None,
        {
            "pageNumber": 2,
            "pageSize": 25,
            "sortDirection": "DESC",
            "ownerIds": [RECORD_ID, PARTICIPANT_ID],
            "hasPendingChecklistItems": False,
            "searchText": "Test buyer",
        },
    ],
)
@responses.activate
def test_search_preserves_native_filters(params: Any) -> None:
    """Send native filters, including repeated IDs and false, without coercion."""
    page = {
        "pageNumber": 2,
        "pageSize": 25,
        "hasNext": False,
        "totalCount": 0,
        "buyerRecords": [],
    }
    responses.add(responses.GET, f"{BASE_URL}/buyer-record", json=page)
    client = BuyerRecordsClient(api_key="test-key")
    result = (
        client.search_buyer_records()
        if params is None
        else client.search_buyer_records(params)
    )
    assert result == page
    query = parse_qs(urlparse(responses.calls[0].request.url).query)
    expected = (
        {}
        if params is None
        else {
            "pageNumber": ["2"],
            "pageSize": ["25"],
            "sortDirection": ["DESC"],
            "ownerIds": [RECORD_ID, PARTICIPANT_ID],
            "hasPendingChecklistItems": ["False"],
            "searchText": ["Test buyer"],
        }
    )
    assert query == expected


@responses.activate
def test_buyer_conversion_and_dual_association_sequence() -> None:
    """Use returned record/builder IDs without the deprecated direct POST."""
    client = RezenClient(api_key="test-key")
    builder = {"id": "builder-id", "buyerRecordId": RECORD_ID}
    associations = {"buyerRecordId": RECORD_ID, "listingId": "listing-id"}
    responses.add(
        responses.POST, f"{BASE_URL}/buyer-record", json={"id": RECORD_ID}, status=201
    )
    responses.add(
        responses.POST,
        f"{BASE_URL}/buyer-record/{RECORD_ID}/build-transaction",
        json=builder,
    )
    responses.add(
        responses.PATCH,
        f"{BASE_URL}/transaction-builder/builder-id/associations",
        json=builder,
    )
    record = client.buyer_records.create_buyer_record(CREATE_DATA)
    converted = client.buyer_records.build_transaction(record["id"])
    assert (
        client.transaction_builder.update_associations(converted["id"], associations)
        == builder
    )
    assert json.loads(responses.calls[2].request.body) == associations
    assert [call.request.method for call in responses.calls] == [
        "POST",
        "POST",
        "PATCH",
    ]


@responses.activate
def test_buyer_record_validation_failure_propagates() -> None:
    """Surface API validation errors without creating a fallback builder."""
    responses.add(
        responses.POST,
        f"{BASE_URL}/buyer-record",
        json={"message": "bbaDates is required"},
        status=400,
    )
    with pytest.raises(ValidationError, match="bbaDates is required"):
        RezenClient(api_key="test-key").buyer_records.create_buyer_record({})
    assert len(responses.calls) == 1


def test_lazy_buyer_records_client_inherits_all_options() -> None:
    """Cache the public subclient and forward custom transport settings."""
    client = RezenClient(
        api_key="test-key",
        base_url="https://example.com/api/v1",
        timeout_seconds=12,
        max_retries=2,
        retry_backoff_seconds=0.1,
    )
    assert client._buyer_records is None
    buyer_records = client.buyer_records
    assert isinstance(buyer_records, BuyerRecordsClient)
    assert client.buyer_records is buyer_records
    assert buyer_records.api_key == "test-key"
    assert buyer_records.base_url == "https://example.com/api/v1"
    assert buyer_records.timeout_seconds == 12
    assert buyer_records.max_retries == 2
    assert buyer_records.retry_backoff_seconds == 0.1


def test_buyer_records_client_uses_environment_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Preserve standard environment authentication for the new subclient."""
    monkeypatch.setenv("REZEN_API_KEY", "environment-test-key")
    assert RezenClient().buyer_records.api_key == "environment-test-key"
