"""Buyer Record endpoints for the Arrakis ReZEN API."""

from typing import Any, Dict, Optional

from .base_client import BaseClient


class BuyerRecordsClient(BaseClient):
    """Manage pre-contract Buyer Records and convert them to transaction builders."""

    def create_buyer_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Buyer Record using the API's camelCase request fields.

        Args:
            data: Request containing officeId, geographicInterest, bbaDates
                (start/end ISO dates), and initialParticipants. Participant entries
                wrap internalParticipant or externalParticipant; external email
                uses emailAddress. Optional fields include teamId/createOnBehalfOf.

        Returns:
            The created Buyer Record, including its id.
        """
        return self.post("buyer-record", json_data=data)

    def search_buyer_records(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search Buyer Records with native pagination, sorting, and filters.

        Args:
            params: API query fields, such as pageNumber, pageSize, sortBy,
                sortDirection, ownerIds, lifecycleStates, officeIds, or searchText.

        Returns:
            Page metadata and the buyerRecords collection.
        """
        return self.get("buyer-record", params=params)

    def get_buyer_record(self, buyer_record_id: str) -> Dict[str, Any]:
        """Retrieve a Buyer Record.

        Args:
            buyer_record_id: Buyer Record UUID.

        Returns:
            Buyer Record details and participants.
        """
        return self.get(f"buyer-record/{buyer_record_id}")

    def update_buyer_record(
        self, buyer_record_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update Buyer Record details.

        Args:
            buyer_record_id: Buyer Record UUID.
            data: Fields to update, such as bbaDates, geographicInterest,
                officeId, or teamId.

        Returns:
            An empty dictionary for the API's successful 204 response.
        """
        return self.patch(f"buyer-record/{buyer_record_id}", json_data=data)

    def add_participant(
        self, buyer_record_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add an internal or external participant to a Buyer Record.

        Args:
            buyer_record_id: Buyer Record UUID.
            data: An internalParticipant or externalParticipant wrapper. Creation
                uses role; external participants also need externalParticipantType.

        Returns:
            Updated Buyer Record details.
        """
        return self.post(f"buyer-record/{buyer_record_id}/participant", json_data=data)

    def update_participant(
        self, buyer_record_id: str, participant_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a Buyer Record participant.

        Args:
            buyer_record_id: Buyer Record UUID.
            participant_id: Participant UUID.
            data: An internalParticipant or externalParticipant wrapper. Role
                updates use participantRole, rather than the creation field role.

        Returns:
            An empty dictionary for the API's successful 204 response.
        """
        return self.patch(
            f"buyer-record/{buyer_record_id}/participant/{participant_id}",
            json_data=data,
        )

    def delete_participant(
        self, buyer_record_id: str, participant_id: str
    ) -> Dict[str, Any]:
        """Remove a Buyer Record participant.

        Args:
            buyer_record_id: Buyer Record UUID.
            participant_id: Participant UUID.

        Returns:
            An empty dictionary for the API's successful 204 response.
        """
        return self.delete(
            f"buyer-record/{buyer_record_id}/participant/{participant_id}"
        )

    def build_transaction(self, buyer_record_id: str) -> Dict[str, Any]:
        """Convert a Buyer Record to a transaction builder without a request body.

        Args:
            buyer_record_id: Buyer Record UUID.

        Returns:
            Transaction builder details, including id and buyerRecordId.
        """
        return self.post(f"buyer-record/{buyer_record_id}/build-transaction")

    def request_termination(self, buyer_record_id: str, reason: str) -> Dict[str, Any]:
        """Request Buyer Record termination.

        Args:
            buyer_record_id: Buyer Record UUID.
            reason: Termination reason, up to 255 characters.

        Returns:
            An empty dictionary for the API's successful 204 response.
        """
        return self.patch(
            f"buyer-record/{buyer_record_id}/request-termination",
            json_data={"reason": reason},
        )

    def cancel_termination_request(self, buyer_record_id: str) -> Dict[str, Any]:
        """Cancel a pending termination request without a request body.

        Args:
            buyer_record_id: Buyer Record UUID.

        Returns:
            An empty dictionary for the API's successful 204 response.
        """
        return self.patch(f"buyer-record/{buyer_record_id}/cancel-termination-request")
