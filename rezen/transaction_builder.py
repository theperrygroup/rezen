"""Transaction Builder client for ReZEN API."""

from typing import Any, BinaryIO, Dict, List, Optional

from .base_client import BaseClient
from .exceptions import (
    InvalidFieldNameError,
    InvalidFieldValueError,
    TransactionSequenceError,
    ValidationError,
)


class TransactionBuilderClient(BaseClient):
    """Client for transaction builder endpoints."""

    def update_title_info(
        self, transaction_id: str, title_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update title details for a transaction builder.

        Important: Use camelCase for field names:
        - firstName (not first_name)
        - lastName (not last_name)
        - phoneNumber (not phone_number)

        Example:
            title_info = {
                "company": "Premier Title Company",
                "firstName": "Sarah",
                "lastName": "Johnson",
                "email": "sarah@premiertitle.com",
                "phoneNumber": "(555) 555-5555"
            }

        Args:
            transaction_id: Transaction builder ID
            title_info: Title information data with camelCase fields

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/title"
        return self.put(endpoint, json_data=title_info)

    def add_seller(
        self, transaction_id: str, seller_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a new seller to a transaction builder.

        Important: Use camelCase for field names:
        - firstName (not first_name)
        - lastName (not last_name)
        - phoneNumber (not phone_number)

        Example:
            seller_info = {
                "firstName": "Jane",
                "lastName": "Smith",
                "email": "jane.smith@example.com",
                "phoneNumber": "(555) 987-6543"
            }

        Args:
            transaction_id: Transaction builder ID
            seller_info: Seller information data with camelCase fields

        Returns:
            Transaction builder response data
        """
        # Check for common field name errors
        field_mappings = {
            "first_name": "firstName",
            "last_name": "lastName",
            "phone_number": "phoneNumber",
            "phone": "phoneNumber",
        }

        for snake, camel in field_mappings.items():
            if snake in seller_info:
                raise InvalidFieldNameError(
                    snake, camel, "Use camelCase for seller fields."
                )

        endpoint = f"transaction-builder/{transaction_id}/seller"
        return self.put(endpoint, json_data=seller_info)

    def add_referral_info(
        self,
        transaction_id: str,
        role: str,
        receives_invoice: bool,
        referral_type: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company_name: Optional[str] = None,
        email: Optional[str] = None,
        ein: Optional[str] = None,
        phone_number: Optional[str] = None,
        address: Optional[str] = None,
        agent_id: Optional[str] = None,
        file: Optional[BinaryIO] = None,
    ) -> Dict[str, Any]:
        """Add referral info to a transaction builder.

        Note: This endpoint is marked as deprecated in the API specification.

        Args:
            transaction_id: Transaction builder ID
            role: Role type (e.g., 'REAL', 'BUYERS_AGENT', 'SELLERS_AGENT', etc.)
            receives_invoice: Whether the referral receives invoice
            referral_type: Type of referral ('EXTERNAL_ENTITY' or 'AGENT')
            first_name: First name (optional)
            last_name: Last name (optional)
            company_name: Company name (optional)
            email: Email address (optional)
            ein: EIN number (optional)
            phone_number: Phone number (optional)
            address: Address (optional)
            agent_id: Agent ID (optional)
            file: File to upload (optional)

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/referral-info"
        params = {
            "role": role,
            "receivesInvoice": receives_invoice,
            "type": referral_type,
        }

        # Add optional parameters
        if first_name:
            params["firstName"] = first_name
        if last_name:
            params["lastName"] = last_name
        if company_name:
            params["companyName"] = company_name
        if email:
            params["email"] = email
        if ein:
            params["ein"] = ein
        if phone_number:
            params["phoneNumber"] = phone_number
        if address:
            params["address"] = address
        if agent_id:
            params["agentId"] = agent_id

        files = {"file": file} if file else None
        return self._request("PUT", endpoint, params=params, files=files)

    def upload_w9_to_referral_participant(
        self, transaction_id: str, participant_id: str, file: BinaryIO
    ) -> Dict[str, Any]:
        """Upload W9 to external referral participant.

        Args:
            transaction_id: Transaction builder ID
            participant_id: Participant ID
            file: W9 file to upload

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/referral-info/{participant_id}/upload-w9"
        files = {"file": file}
        return self.put(endpoint, files=files)

    def update_price_and_date_info(
        self, transaction_id: str, price_date_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update price and date information.

        CRITICAL: This endpoint requires specific field names and structures:
        - salePrice MUST be an object with 'amount' and 'currency', NOT a simple number
        - All dates use camelCase format: acceptanceDate, closingDate, etc.
        - representationType determines valid agent roles (BUYER → BUYERS_AGENT, SELLER → SELLERS_AGENT)

        Required Fields:
            - dealType (str): "COMPENSATING" or "NON_COMPENSATING"
            - propertyType (str): "RESIDENTIAL", "COMMERCIAL", etc.
            - salePrice (dict): {"amount": 500000, "currency": "USD"}
            - representationType (str): "BUYER" or "SELLER" - affects owner agent role

        Optional Fields:
            - listingCommission (dict): {"commissionPercent": 3.0, "percentEnabled": true}
            - saleCommission (dict): {"commissionPercent": 3.0, "percentEnabled": true}
            - acceptanceDate (str): Date in "YYYY-MM-DD" format
            - closingDate (str): Date in "YYYY-MM-DD" format
            - earnestMoney (float): Earnest money amount
            - downPayment (float): Down payment amount
            - loanAmount (float): Loan amount

        Example:
            ```python
            price_date_info = {
                "dealType": "COMPENSATING",
                "propertyType": "RESIDENTIAL",
                "salePrice": {
                    "amount": 565000,
                    "currency": "USD"
                },
                "listingCommission": {
                    "commissionPercent": 3.0,
                    "percentEnabled": True,
                    "negativeOrEmpty": False
                },
                "saleCommission": {
                    "commissionPercent": 3.0,
                    "percentEnabled": True,
                    "negativeOrEmpty": False
                },
                "acceptanceDate": "2024-01-15",
                "closingDate": "2024-02-28",
                "representationType": "BUYER"  # This must match owner agent role
            }
            ```

        Args:
            transaction_id: Transaction builder ID
            price_date_info: Price and date information data with proper structure

        Returns:
            Transaction builder response data
        """
        # Validate required fields
        required_fields = [
            "dealType",
            "propertyType",
            "salePrice",
            "representationType",
        ]
        missing_fields = [
            field for field in required_fields if field not in price_date_info
        ]
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}. "
                f"All of these are required: {', '.join(required_fields)}"
            )

        # Validate salePrice structure
        if "salePrice" in price_date_info:
            sale_price = price_date_info["salePrice"]
            if isinstance(sale_price, (int, float)):
                raise InvalidFieldValueError(
                    "salePrice",
                    sale_price,
                    "Object with 'amount' and 'currency' fields: {'amount': 500000, 'currency': 'USD'}",
                )
            elif isinstance(sale_price, dict):
                if "amount" not in sale_price or "currency" not in sale_price:
                    raise InvalidFieldValueError(
                        "salePrice",
                        sale_price,
                        "Object must contain both 'amount' and 'currency' fields",
                    )

        # Validate representationType values
        if "representationType" in price_date_info:
            rep_type = price_date_info["representationType"]
            valid_types = ["BUYER", "SELLER"]
            if rep_type not in valid_types:
                raise InvalidFieldValueError(
                    "representationType",
                    rep_type,
                    f"One of: {', '.join(valid_types)} (Note: Use 'BUYER' not 'BUYERS_AGENT')",
                )

        # Check for common date field errors
        date_fields = {
            "acceptance_date": "acceptanceDate",
            "closing_date": "closingDate",
        }
        for snake, camel in date_fields.items():
            if snake in price_date_info:
                raise InvalidFieldNameError(
                    snake, camel, "Use camelCase for date fields."
                )

        endpoint = f"transaction-builder/{transaction_id}/price-date-info"
        return self.put(endpoint, json_data=price_date_info)

    def update_personal_deal_info(
        self, transaction_id: str, deal_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update personal deal information.

        Sets whether this transaction is a personal deal (agent buying/selling own property).

        Required Fields:
            - isPersonalDeal (bool): Whether this is a personal deal

        Example:
            ```python
            deal_info = {
                "isPersonalDeal": True  # Agent is buying/selling their own property
            }
            client.update_personal_deal_info(transaction_id, deal_info)
            ```

        Args:
            transaction_id: Transaction builder ID
            deal_info: Personal deal information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/personal-deal-info"
        return self.put(endpoint, json_data=deal_info)

    def update_owner_info(
        self, transaction_id: str, owner_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update owner agent information.

        Args:
            transaction_id: Transaction builder ID
            owner_info: Owner agent information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/owner-info"
        return self.put(endpoint, json_data=owner_info)

    def add_participant(
        self, transaction_id: str, participant_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a new participant to the transaction builder.

        Args:
            transaction_id: Transaction builder ID
            participant_info: Participant information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/other-participants"
        # This endpoint uses multipart/form-data according to the schema
        return self._request("PUT", endpoint, data=participant_info)

    def add_opcity(self, transaction_id: str, opcity: bool) -> Dict[str, Any]:
        """Add opcity to transaction builder.

        Args:
            transaction_id: Transaction builder ID
            opcity: Whether to enable opcity

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/opcity"
        params = {"opcity": opcity}
        return self._request("PUT", endpoint, params=params)

    def update_mortgage_info(
        self, transaction_id: str, mortgage_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update mortgage information.

        Args:
            transaction_id: Transaction builder ID
            mortgage_info: Mortgage information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/mortgage-info"
        return self.put(endpoint, json_data=mortgage_info)

    def update_location_info(
        self, transaction_id: str, location_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update location information.

        Important: The API requires specific field names and formats:
        - Use 'street' not 'address'
        - Use 'zip' not 'zipCode'
        - State must be 'UTAH' (all caps)
        - Use camelCase for: yearBuilt, mlsNumber, escrowNumber

        Example:
            location_info = {
                "street": "123 Main Street",
                "street2": "",
                "city": "Salt Lake City",
                "state": "UTAH",
                "zip": "84101",
                "county": "Salt Lake",
                "unit": "",
                "yearBuilt": 2020,
                "mlsNumber": "MLS123456",
                "escrowNumber": "ESC-2024-001"
            }

        Args:
            transaction_id: Transaction builder ID
            location_info: Location information data with required fields

        Returns:
            Transaction builder response data
        """
        # Check for common field name errors
        if "address" in location_info:
            raise InvalidFieldNameError(
                "address",
                "street",
                "The API expects 'street' for the property address.",
            )

        if "zipCode" in location_info or "zip_code" in location_info:
            raise InvalidFieldNameError(
                "zipCode/zip_code", "zip", "The API expects 'zip' for the ZIP code."
            )

        # Validate state format if present
        if "state" in location_info:
            state = location_info["state"]
            # Check if it's lowercase or mixed case
            if state and state != state.upper():
                raise InvalidFieldValueError(
                    "state",
                    state,
                    "State code in ALL CAPS (e.g., 'UTAH', 'CALIFORNIA')",
                )

        # Check for snake_case field names
        snake_case_fields = {
            "year_built": "yearBuilt",
            "mls_number": "mlsNumber",
            "escrow_number": "escrowNumber",
        }
        for snake, camel in snake_case_fields.items():
            if snake in location_info:
                raise InvalidFieldNameError(
                    snake, camel, "Use camelCase for property fields."
                )

        endpoint = f"transaction-builder/{transaction_id}/location-info"
        return self.put(endpoint, json_data=location_info)

    def update_fmls_info(
        self, transaction_id: str, fmls_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update whether this builder's property is listed on FMLS.

        Args:
            transaction_id: Transaction builder ID
            fmls_info: FMLS information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/fmls"
        return self.put(endpoint, json_data=fmls_info)

    def add_double_ender_agent(
        self, transaction_id: str, agent_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add double-ender agent to the transaction builder.

        Args:
            transaction_id: Transaction builder ID
            agent_info: Double-ender agent information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/double-ender-agent"
        return self.put(endpoint, json_data=agent_info)

    def add_commission_payer(
        self, transaction_id: str, commission_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add commission payer information.

        IMPORTANT: This endpoint requires multipart/form-data format.
        The method automatically handles the conversion for you.

        Required Fields:
            - role (str): Commission payer role (e.g., "REAL", "NA", "LISTING_AGENT", "BUYERS_AGENT")

        Optional Fields:
            - receivesInvoice (bool): Whether the payer receives invoice
            - opCityReferral (bool): Whether this is an OpCity referral
            - optedInForEcp (bool): Whether opted in for ECP

        Special Note:
            Based on testing, the "role" field accepts specific values that may differ
            from what's shown in API documentation. Common working values include:
            - "REAL" - For standard commission payers
            - "NA" - Not applicable/none
            - Role values matching agent roles (LISTING_AGENT, BUYERS_AGENT, etc.)

        Example:
            ```python
            commission_info = {
                "role": "REAL",
                "receivesInvoice": True,
                "opCityReferral": False,
                "optedInForEcp": False
            }
            client.add_commission_payer(transaction_id, commission_info)
            ```

        Args:
            transaction_id: Transaction builder ID
            commission_info: Commission payer information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/commission-payer"
        # This endpoint requires multipart/form-data
        # Convert form data to files format to force multipart
        files = {key: (None, str(value)) for key, value in commission_info.items()}
        return self._request("PUT", endpoint, files=files)

    def update_commission_splits(
        self, transaction_id: str, commission_splits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update commission splits information.

        IMPORTANT: Pass a LIST of commission split objects, even for a single split.

        Commission Split Structure:
            Each split in the list should contain:
            - agentId (str): UUID of the agent receiving the split
            - receivesInvoice (bool): Whether this agent receives an invoice
            - splitPercent (float): Percentage of commission (e.g., 50.0 for 50%)
            - opCityReferral (bool): Whether this is an OpCity referral (optional)
            - optedInForEcp (bool): Whether opted in for ECP (optional)

        Example:
            ```python
            commission_splits = [
                {
                    "agentId": "agent-uuid-1",
                    "receivesInvoice": True,
                    "splitPercent": 50.0,
                    "opCityReferral": False,
                    "optedInForEcp": False
                },
                {
                    "agentId": "agent-uuid-2",
                    "receivesInvoice": False,
                    "splitPercent": 50.0,
                    "opCityReferral": False,
                    "optedInForEcp": False
                }
            ]
            client.update_commission_splits(transaction_id, commission_splits)
            ```

        Args:
            transaction_id: Transaction builder ID
            commission_splits: List of commission split data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/commission-info"
        return self._request("PUT", endpoint, json_data=commission_splits)

    def update_owner_agent_info(
        self, transaction_builder_id: str, owner_agent_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update owner agent information for the transaction.

        ⚠️ CRITICAL SEQUENCE REQUIREMENT ⚠️
        This endpoint REQUIRES the transaction to be set up in this EXACT order:
        1. Create transaction (create_transaction_builder)
        2. Add location info (update_location_info) - REQUIRED FIRST
        3. Add price/date info (update_price_and_date_info) - REQUIRED SECOND
        4. Add buyers/sellers (add_buyer/add_seller) - REQUIRED THIRD
        5. THEN add owner agent (this method) - NOW IT WORKS!

        If you call this endpoint before completing steps 1-4, it will return
        "Bad request: Invalid request" even with correct data.

        Data Structure:
            owner_agent_info = {
                "ownerAgent": {
                    "agentId": str,  # UUID of the agent
                    "role": str      # "BUYERS_AGENT" or "SELLERS_AGENT"
                },
                "officeId": str,     # UUID of the office (optional)
                "teamId": str        # UUID of the team (optional)
            }

        Role Matching:
            The role MUST match the representationType from price/date info:
            - representationType: "BUYER" → role: "BUYERS_AGENT"
            - representationType: "SELLER" → role: "SELLERS_AGENT"

        Example - Complete Working Sequence:
            ```python
            # 1. Create transaction
            builder_id = client.create_transaction_builder()

            # 2. Add location (REQUIRED FIRST)
            client.update_location_info(builder_id, {
                "street": "123 Main St",
                "city": "Salt Lake City",
                "state": "UTAH",
                "zip": "84101"
            })

            # 3. Add price/date (REQUIRED SECOND)
            client.update_price_and_date_info(builder_id, {
                "dealType": "COMPENSATING",
                "propertyType": "RESIDENTIAL",
                "salePrice": {"amount": 500000, "currency": "USD"},
                "representationType": "BUYER"  # Note: BUYER not BUYERS_AGENT
            })

            # 4. Add buyer (REQUIRED THIRD)
            client.add_buyer(builder_id, {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john@example.com",
                "phoneNumber": "(555) 123-4567"
            })

            # 5. NOW add owner agent (WORKS!)
            owner_info = {
                "ownerAgent": {
                    "agentId": "your-agent-uuid",
                    "role": "BUYERS_AGENT"  # Must match representationType
                },
                "officeId": "your-office-uuid",
                "teamId": "your-team-uuid"
            }
            result = client.update_owner_agent_info(builder_id, owner_info)
            ```

        Args:
            transaction_builder_id: UUID of the transaction builder
            owner_agent_info: Dictionary containing owner agent details

        Returns:
            Updated transaction builder data

        Raises:
            ValidationError: If owner agent info is invalid or sequence not followed
            NotFoundError: If transaction builder not found
        """
        # Validate required structure
        if "ownerAgent" not in owner_agent_info:
            raise ValidationError(
                "Missing required field 'ownerAgent'. Expected structure: "
                "{'ownerAgent': {'agentId': 'uuid', 'role': 'BUYERS_AGENT'}, "
                "'officeId': 'uuid', 'teamId': 'uuid'}"
            )

        owner_agent = owner_agent_info["ownerAgent"]
        if not isinstance(owner_agent, dict):
            raise InvalidFieldValueError(
                "ownerAgent", owner_agent, "Object with 'agentId' and 'role' fields"
            )

        # Validate ownerAgent fields
        if "agentId" not in owner_agent:
            raise ValidationError("Missing required field 'agentId' in ownerAgent")
        if "role" not in owner_agent:
            raise ValidationError("Missing required field 'role' in ownerAgent")

        # Validate role value
        role = owner_agent["role"]
        valid_roles = ["BUYERS_AGENT", "SELLERS_AGENT"]
        if role not in valid_roles:
            raise InvalidFieldValueError(
                "role",
                role,
                f"One of: {', '.join(valid_roles)} (Must match representationType: BUYER→BUYERS_AGENT, SELLER→SELLERS_AGENT)",
            )

        endpoint = f"transaction-builder/{transaction_builder_id}/owner-info"

        try:
            return self.put(endpoint, json_data=owner_agent_info)
        except ValidationError as e:
            # If we get a generic "Bad request" error, provide more helpful context
            if "Invalid request" in str(e):
                raise TransactionSequenceError(
                    "Owner agent endpoint failed. This usually means the transaction isn't properly set up yet.",
                    required_steps=[
                        "Create transaction (create_transaction_builder)",
                        "Add location info (update_location_info) - REQUIRED FIRST",
                        "Add price/date info (update_price_and_date_info) with representationType - REQUIRED SECOND",
                        "Add buyers/sellers (add_buyer/add_seller) - REQUIRED THIRD",
                        "THEN add owner agent (update_owner_agent_info)",
                    ],
                )
            raise  # Re-raise if it's a different error

    def add_co_agent(
        self, transaction_id: str, co_agent_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a new co-agent.

        Required Fields:
            - agentId (str): UUID of the co-agent
            - role (str): Agent role (e.g., "REAL", "BUYERS_AGENT", "SELLERS_AGENT")
            - receivesInvoice (bool): Whether the co-agent receives invoice

        Optional Fields:
            - opCityReferral (bool): Whether this is an OpCity referral
            - optedInForEcp (bool): Whether opted in for ECP

        Example:
            ```python
            co_agent_info = {
                "agentId": "agent-uuid-here",
                "role": "REAL",
                "receivesInvoice": False
            }
            client.add_co_agent(transaction_id, co_agent_info)
            ```

        Args:
            transaction_id: Transaction builder ID
            co_agent_info: Co-agent information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/co-agent"
        return self.put(endpoint, json_data=co_agent_info)

    def add_buyer(
        self, transaction_id: str, buyer_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a new buyer.

        Important: Use camelCase for field names:
        - firstName (not first_name)
        - lastName (not last_name)
        - phoneNumber (not phone_number)

        Example:
            buyer_info = {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "phoneNumber": "(555) 123-4567"
            }

        Args:
            transaction_id: Transaction builder ID
            buyer_info: Buyer information data with camelCase fields

        Returns:
            Transaction builder response data
        """
        # Check for common field name errors
        field_mappings = {
            "first_name": "firstName",
            "last_name": "lastName",
            "phone_number": "phoneNumber",
            "phone": "phoneNumber",
        }

        for snake, camel in field_mappings.items():
            if snake in buyer_info:
                raise InvalidFieldNameError(
                    snake, camel, "Use camelCase for buyer fields."
                )

        endpoint = f"transaction-builder/{transaction_id}/buyer"
        return self.put(endpoint, json_data=buyer_info)

    def update_buyer_and_seller_info(
        self, transaction_id: str, buyer_seller_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update buyer and seller information.

        Args:
            transaction_id: Transaction builder ID
            buyer_seller_info: Buyer and seller information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/buyer-seller-info"
        return self.put(endpoint, json_data=buyer_seller_info)

    def update_additional_fees_info(
        self, transaction_id: str, fees_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update additional fees information.

        Args:
            transaction_id: Transaction builder ID
            fees_info: Additional fees information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/additional-fees-info"
        return self.put(endpoint, json_data=fees_info)

    def add_referral_info_v2(
        self, transaction_id: str, referral_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add referral info (v2 endpoint).

        Args:
            transaction_id: Transaction builder ID
            referral_info: Referral information data

        Returns:
            Builder participant data
        """
        endpoint = f"transaction-builder/{transaction_id}/add-referral-info"
        return self.put(endpoint, json_data=referral_info)

    # GET endpoints
    def get_transaction_builders(
        self,
        limit: int,
        from_offset: int,
        yenta_id: str,
        builder_type: str = "TRANSACTION",
    ) -> Dict[str, Any]:
        """Get a paginated list of transaction builders.

        Args:
            limit: Maximum number of results to return
            from_offset: Starting offset for pagination
            yenta_id: User ID
            builder_type: Type of builder ('TRANSACTION' or 'LISTING')

        Returns:
            Paginated list of transaction builders
        """
        endpoint = "transaction-builder"
        params = {
            "limit": limit,
            "from": from_offset,
            "yentaId": yenta_id,
            "type": builder_type,
        }
        return self.get(endpoint, params=params)

    def get_transaction_builders_paged(
        self,
        limit: int,
        from_offset: int,
        yenta_id: str,
        builder_type: str = "TRANSACTION",
    ) -> Dict[str, Any]:
        """Get a paginated list of transaction builders (alternative endpoint).

        Args:
            limit: Maximum number of results to return
            from_offset: Starting offset for pagination
            yenta_id: User ID
            builder_type: Type of builder ('TRANSACTION' or 'LISTING')

        Returns:
            Paginated list of transaction builders
        """
        endpoint = "transaction-builder/paged"
        params = {
            "limit": limit,
            "from": from_offset,
            "yentaId": yenta_id,
            "type": builder_type,
        }
        return self.get(endpoint, params=params)

    def get_transaction_builder(self, transaction_id: str) -> Dict[str, Any]:
        """Get a specific transaction builder by ID.

        Args:
            transaction_id: Transaction builder ID

        Returns:
            Transaction builder data
        """
        endpoint = f"transaction-builder/{transaction_id}"
        return self.get(endpoint)

    def get_builder_features(self, transaction_id: str) -> Dict[str, Any]:
        """Get optional features available for the transaction being built.

        Args:
            transaction_id: Transaction builder ID

        Returns:
            Available features data
        """
        endpoint = f"transaction-builder/{transaction_id}/features"
        return self.get(endpoint)

    def get_eligible_for_mortgage_ecp(self, transaction_id: str) -> Dict[str, Any]:
        """Check if transaction builder is eligible for mortgage ECP.

        Args:
            transaction_id: Transaction builder ID

        Returns:
            Eligibility status
        """
        endpoint = f"transaction-builder/{transaction_id}/eligible-for-mortgage-ecp"
        return self.get(endpoint)

    def get_commission_payer_roles_and_display_name(
        self, transaction_id: str
    ) -> Dict[str, Any]:
        """Get commission payer roles and display names for transaction builder.

        Args:
            transaction_id: Transaction builder ID

        Returns:
            Commission payer roles and display names
        """
        endpoint = f"transaction-builder/{transaction_id}/commission-payer-roles-and-display-name"
        return self.get(endpoint)

    def get_commission_payer_roles(
        self, country: str = "UNITED_STATES"
    ) -> Dict[str, Any]:
        """Get available commission payer roles.

        Args:
            country: Country code (default: "UNITED_STATES")

        Returns:
            Available commission payer roles
        """
        endpoint = "transaction-builder/commission-payer-roles"
        params = {"country": country}
        return self.get(endpoint, params=params)

    def get_commission_payer_roles_and_display_names(
        self, country: str = "UNITED_STATES", representation_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get commission payer roles and their display names.

        Args:
            country: Country code (default: "UNITED_STATES")
            representation_type: Type of representation (e.g., "SELLER", "BUYER")

        Returns:
            Commission payer roles with display names
        """
        endpoint = "transaction-builder/commission-payer-roles-and-display-name"
        params = {"country": country}
        if representation_type:
            params["representationType"] = representation_type
        return self.get(endpoint, params=params)

    def get_metadata_for_participant_creation(
        self, transaction_id: str, participant_role: str
    ) -> Dict[str, Any]:
        """Get metadata required to create a participant.

        Args:
            transaction_id: Transaction builder ID
            participant_role: Role of the participant to be created

        Returns:
            Metadata for participant creation
        """
        endpoint = f"transaction-builder/{transaction_id}/metadata-for-participant-creation/{participant_role}"
        return self.get(endpoint)

    # POST endpoints
    def create_transaction_builder(self, builder_type: str = "TRANSACTION") -> str:
        """Create empty transaction builder.

        Args:
            builder_type: Type of builder ('TRANSACTION' or 'LISTING')

        Returns:
            Transaction builder ID
        """
        endpoint = "transaction-builder"
        params = {"type": builder_type}
        response = self._request("POST", endpoint, params=params)
        # Extract ID from response
        if isinstance(response, dict):
            if "id" in response:
                return str(response["id"])
            elif "message" in response:
                return str(response["message"])
        return str(response)

    def create_listing_builder(self) -> str:
        """Create a listing builder (wrapper for create_transaction_builder).

        Returns:
            Listing builder ID
        """
        return self.create_transaction_builder(builder_type="LISTING")

    def convert_listing_to_transaction(self, listing_id: str) -> Dict[str, Any]:
        """Convert a listing to a transaction (wrapper for create_builder_from_transaction).

        Args:
            listing_id: Listing ID to convert

        Returns:
            Transaction builder response data
        """
        return self.create_builder_from_transaction(listing_id)

    def create_builder_from_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Create transaction builder from given transaction.

        Args:
            transaction_id: Transaction ID to create builder from

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/transaction-to-builder"
        return self.post(endpoint)

    def add_transaction_coordinator(
        self, transaction_id: str, yenta_id: str
    ) -> Dict[str, Any]:
        """Add transaction coordinator to transaction builder.

        Args:
            transaction_id: Transaction builder ID
            yenta_id: Coordinator user ID

        Returns:
            Transaction builder response data
        """
        endpoint = (
            f"transaction-builder/{transaction_id}/transaction-coordinator/{yenta_id}"
        )
        return self.post(endpoint)

    def submit_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Submit a transaction builder to create a transaction.

        Args:
            transaction_id: Transaction builder ID

        Returns:
            Transaction preview response data
        """
        endpoint = f"transaction-builder/{transaction_id}/submit"
        return self.post(endpoint)

    def update_title_contract(
        self, transaction_id: str, title_contract_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update title contract information.

        Args:
            transaction_id: Transaction builder ID
            title_contract_info: Title contract information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/title-contract"
        return self.put(endpoint, json_data=title_contract_info)

    def mortgage_ecp_opt_out(self, transaction_id: str) -> Dict[str, Any]:
        """Opt out of mortgage ECP for transaction builder.

        Args:
            transaction_id: Transaction builder ID

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/mortgage-ecp-opt-out"
        return self.put(endpoint)

    def mortgage_ecp_opt_in(self, transaction_id: str) -> Dict[str, Any]:
        """Opt in to mortgage ECP for transaction builder.

        Args:
            transaction_id: Transaction builder ID

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/mortgage-ecp-opt-in"
        return self.put(endpoint)

    # DELETE endpoints
    def delete_transaction_builder(self, transaction_id: str) -> Dict[str, Any]:
        """Delete transaction builder.

        Args:
            transaction_id: Transaction builder ID

        Returns:
            Deletion response data
        """
        endpoint = f"transaction-builder/{transaction_id}"
        return self.delete(endpoint)

    # Individual resource endpoints
    def get_seller(self, transaction_id: str, seller_id: str) -> Dict[str, Any]:
        """Get specific seller information.

        Args:
            transaction_id: Transaction builder ID
            seller_id: Seller ID

        Returns:
            Seller data
        """
        endpoint = f"transaction-builder/{transaction_id}/seller/{seller_id}"
        return self.get(endpoint)

    def update_seller(
        self, transaction_id: str, seller_id: str, seller_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update specific seller information.

        Args:
            transaction_id: Transaction builder ID
            seller_id: Seller ID
            seller_info: Updated seller information

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/seller/{seller_id}"
        return self.put(endpoint, json_data=seller_info)

    def delete_seller(self, transaction_id: str, seller_id: str) -> Dict[str, Any]:
        """Delete specific seller.

        Args:
            transaction_id: Transaction builder ID
            seller_id: Seller ID

        Returns:
            Deletion response data
        """
        endpoint = f"transaction-builder/{transaction_id}/seller/{seller_id}"
        return self.delete(endpoint)

    def get_referral_participant(
        self, transaction_id: str, participant_id: str
    ) -> Dict[str, Any]:
        """Get specific referral participant information.

        Args:
            transaction_id: Transaction builder ID
            participant_id: Participant ID

        Returns:
            Referral participant data
        """
        endpoint = (
            f"transaction-builder/{transaction_id}/referral-info/{participant_id}"
        )
        return self.get(endpoint)

    def update_referral_participant(
        self, transaction_id: str, participant_id: str, participant_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update specific referral participant information.

        Args:
            transaction_id: Transaction builder ID
            participant_id: Participant ID
            participant_info: Updated participant information

        Returns:
            Transaction builder response data
        """
        endpoint = (
            f"transaction-builder/{transaction_id}/referral-info/{participant_id}"
        )
        return self.put(endpoint, json_data=participant_info)

    def delete_referral_participant(
        self, transaction_id: str, participant_id: str
    ) -> Dict[str, Any]:
        """Delete specific referral participant.

        Args:
            transaction_id: Transaction builder ID
            participant_id: Participant ID

        Returns:
            Deletion response data
        """
        endpoint = (
            f"transaction-builder/{transaction_id}/referral-info/{participant_id}"
        )
        return self.delete(endpoint)

    def get_other_participant(
        self, transaction_id: str, participant_id: str
    ) -> Dict[str, Any]:
        """Get specific other participant information.

        Args:
            transaction_id: Transaction builder ID
            participant_id: Participant ID

        Returns:
            Other participant data
        """
        endpoint = (
            f"transaction-builder/{transaction_id}/other-participants/{participant_id}"
        )
        return self.get(endpoint)

    def update_other_participant(
        self, transaction_id: str, participant_id: str, participant_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update specific other participant information.

        Args:
            transaction_id: Transaction builder ID
            participant_id: Participant ID
            participant_info: Updated participant information

        Returns:
            Transaction builder response data
        """
        endpoint = (
            f"transaction-builder/{transaction_id}/other-participants/{participant_id}"
        )
        return self.put(endpoint, json_data=participant_info)

    def delete_other_participant(
        self, transaction_id: str, participant_id: str
    ) -> Dict[str, Any]:
        """Delete specific other participant.

        Args:
            transaction_id: Transaction builder ID
            participant_id: Participant ID

        Returns:
            Deletion response data
        """
        endpoint = (
            f"transaction-builder/{transaction_id}/other-participants/{participant_id}"
        )
        return self.delete(endpoint)

    def get_co_agent(self, transaction_id: str, co_agent_id: str) -> Dict[str, Any]:
        """Get specific co-agent information.

        Args:
            transaction_id: Transaction builder ID
            co_agent_id: Co-agent ID

        Returns:
            Co-agent data
        """
        endpoint = f"transaction-builder/{transaction_id}/co-agent/{co_agent_id}"
        return self.get(endpoint)

    def update_co_agent(
        self, transaction_id: str, co_agent_id: str, co_agent_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update specific co-agent information.

        Args:
            transaction_id: Transaction builder ID
            co_agent_id: Co-agent ID
            co_agent_info: Updated co-agent information

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/co-agent/{co_agent_id}"
        return self.put(endpoint, json_data=co_agent_info)

    def delete_co_agent(self, transaction_id: str, co_agent_id: str) -> Dict[str, Any]:
        """Delete specific co-agent.

        Args:
            transaction_id: Transaction builder ID
            co_agent_id: Co-agent ID

        Returns:
            Deletion response data
        """
        endpoint = f"transaction-builder/{transaction_id}/co-agent/{co_agent_id}"
        return self.delete(endpoint)

    def get_buyer(self, transaction_id: str, buyer_id: str) -> Dict[str, Any]:
        """Get specific buyer information.

        Args:
            transaction_id: Transaction builder ID
            buyer_id: Buyer ID

        Returns:
            Buyer data
        """
        endpoint = f"transaction-builder/{transaction_id}/buyer/{buyer_id}"
        return self.get(endpoint)

    def update_buyer(
        self, transaction_id: str, buyer_id: str, buyer_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update specific buyer information.

        Args:
            transaction_id: Transaction builder ID
            buyer_id: Buyer ID
            buyer_info: Updated buyer information

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/buyer/{buyer_id}"
        return self.put(endpoint, json_data=buyer_info)

    def delete_buyer(self, transaction_id: str, buyer_id: str) -> Dict[str, Any]:
        """Delete specific buyer.

        Args:
            transaction_id: Transaction builder ID
            buyer_id: Buyer ID

        Returns:
            Deletion response data
        """
        endpoint = f"transaction-builder/{transaction_id}/buyer/{buyer_id}"
        return self.delete(endpoint)

    # Backward compatibility aliases
    def put_buyer_to_draft(
        self, transaction_id: str, buyer_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a new buyer (backward compatibility alias).

        Args:
            transaction_id: Transaction builder ID
            buyer_info: Buyer information data

        Returns:
            Transaction builder response data
        """
        return self.add_buyer(transaction_id, buyer_info)

    def put_seller_to_draft(
        self, transaction_id: str, seller_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a new seller (backward compatibility alias).

        Args:
            transaction_id: Transaction builder ID
            seller_info: Seller information data

        Returns:
            Transaction builder response data
        """
        return self.add_seller(transaction_id, seller_info)

    def put_location_to_draft(
        self, transaction_id: str, location_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update location information (backward compatibility alias).

        Args:
            transaction_id: Transaction builder ID
            location_info: Location information data

        Returns:
            Transaction builder response data
        """
        return self.update_location_info(transaction_id, location_info)

    def put_price_and_date_to_draft(
        self, transaction_id: str, price_date_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update price and date information (backward compatibility alias).

        Args:
            transaction_id: Transaction builder ID
            price_date_info: Price and date information data

        Returns:
            Transaction builder response data
        """
        return self.update_price_and_date_info(transaction_id, price_date_info)

    def update_commission_payer(
        self, transaction_id: str, commission_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update commission payer information (alias for add_commission_payer).

        Args:
            transaction_id: Transaction builder ID
            commission_info: Commission payer information data

        Returns:
            Transaction builder response data
        """
        return self.add_commission_payer(transaction_id, commission_info)

    def update_personal_deal(
        self, transaction_id: str, deal_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update personal deal (alias for update_personal_deal_info).

        Args:
            transaction_id: Transaction builder ID
            deal_info: Personal deal information data

        Returns:
            Transaction builder response data
        """
        return self.update_personal_deal_info(transaction_id, deal_info)

    def update_real_title(
        self, transaction_id: str, title_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update real title (alias for update_title_info).

        Args:
            transaction_id: Transaction builder ID
            title_info: Title information data

        Returns:
            Transaction builder response data
        """
        return self.update_title_info(transaction_id, title_info)

    def set_current_user_as_owner_agent(
        self, transaction_builder_id: str, role: str, users_client: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Set the current authenticated user as the owner agent.

        This is a convenience method that automatically gets the current user's
        information and sets them as the owner agent.

        Args:
            transaction_builder_id: UUID of the transaction builder
            role: Agent role ("BUYERS_AGENT" or "SELLERS_AGENT")
            users_client: Optional UsersClient instance. If None, will create one.

        Returns:
            Updated transaction builder data

        Raises:
            ValidationError: If owner agent info is invalid
            NotFoundError: If transaction builder not found
            AuthenticationError: If not authenticated

        Example:
            ```python
            # Set current user as buyer's agent
            result = client.transaction_builder.set_current_user_as_owner_agent(
                builder_id,
                "BUYERS_AGENT"
            )

            # Set current user as seller's agent with explicit users client
            result = client.transaction_builder.set_current_user_as_owner_agent(
                builder_id,
                "SELLERS_AGENT",
                users_client=client.users
            )
            ```
        """
        # Import here to avoid circular imports
        if users_client is None:
            from .users import UsersClient

            users_client = UsersClient(api_key=self.api_key)

        # Get current user information
        user = users_client.get_current_user()

        # Build owner agent info
        owner_info = {"ownerAgent": {"agentId": user["id"], "role": role}}

        # Add office and team if available
        if user.get("officeId"):
            owner_info["officeId"] = user["officeId"]
        if user.get("teamId"):
            owner_info["teamId"] = user["teamId"]

        return self.update_owner_agent_info(transaction_builder_id, owner_info)
