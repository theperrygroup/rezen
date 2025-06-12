# Transaction Builder API

Create and manage transaction builders with full participant and property management capabilities.

---

## Overview

!!! abstract "Transaction Builder Workflow"

    The Transaction Builder API allows you to:

    - **Create** new transaction builders for various types of real estate transactions
    - **Configure** property details, participants, and financial information
    - **Manage** buyers, sellers, agents, and other transaction participants
    - **Submit** completed transactions for processing
    - **Convert** listings to transactions
    - **Backward Compatibility** with legacy method names

!!! danger "🚨 CRITICAL API REQUIREMENTS"

    **These requirements are MANDATORY for successful API calls:**

    **Location Updates:**
    - Basic address fields (street, city, state, zip) alone will **FAIL**
    - Additional fields are **REQUIRED**: `county`, `yearBuilt`, `mlsNumber`

    **Price/Date Updates:**
    - Basic price fields alone will **FAIL**
    - **BOTH** commission objects are **REQUIRED**: `listingCommission` AND `saleCommission`

    **Co-Agent Roles:**
    - ✅ Working: `"REAL"`, `"BUYERS_AGENT"`, `"SELLERS_AGENT"`
    - ❌ Fails: `"LISTING_AGENT"`

    **Owner Agents:**
    - Require specific sequence: location → price/date → participants → owner agent
    - Need valid `officeId` and `teamId`

---

## Quick Start

=== "🚀 Basic Transaction"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()

    # Step 1: Create transaction builder
    transaction_id: str = client.transaction_builder.create_transaction_builder()

    # Step 2: Add property information - CRITICAL REQUIREMENTS
    # ⚠️ Additional fields beyond basic address are REQUIRED
    location_data: Dict[str, Any] = {
        "street": "123 Main Street",  # Use 'street' not 'address'
        "city": "Salt Lake City",
        "state": "UTAH",  # MUST BE ALL CAPS
        "zip": "84101",   # Use 'zip' not 'zipCode'
        "county": "Salt Lake",      # REQUIRED - API fails without this
        "yearBuilt": 2020,         # REQUIRED - API fails without this
        "mlsNumber": "MLS123456"   # REQUIRED - API fails without this
    }
    client.transaction_builder.update_location_info(transaction_id, location_data)

    # Step 3: Add price/date information - CRITICAL REQUIREMENTS
    # ⚠️ BOTH commission objects are REQUIRED together
    price_data: Dict[str, Any] = {
        "dealType": "COMPENSATING",
        "propertyType": "RESIDENTIAL",
        "salePrice": {"amount": 500000, "currency": "USD"},
        "representationType": "BUYER",
        "listingCommission": {     # REQUIRED - cannot omit
            "commissionPercent": 3.0,
            "percentEnabled": True,
            "negativeOrEmpty": False
        },
        "saleCommission": {        # REQUIRED - cannot omit
            "commissionPercent": 3.0,
            "percentEnabled": True,
            "negativeOrEmpty": False
        }
    }
    client.transaction_builder.update_price_and_date_info(transaction_id, price_data)

    # Step 4: Add participants (use camelCase)
    buyer_data: Dict[str, Any] = {
        "firstName": "John",  # Use camelCase
        "lastName": "Doe",    # Use camelCase
        "email": "john.doe@email.com",
        "phoneNumber": "(555) 123-4567"  # Use camelCase
    }
    client.transaction_builder.add_buyer(transaction_id, buyer_data)

    # Step 5: Add co-agent (working roles only)
    co_agent_data: Dict[str, Any] = {
        "agentId": "bd465129-b224-43e3-b92f-524ea5f53783",
        "role": "REAL",  # ✅ Working role
        "receivesInvoice": False
    }
    client.transaction_builder.add_co_agent(transaction_id, co_agent_data)

    # Step 6: Submit transaction
    client.transaction_builder.submit_transaction(transaction_id)
    ```

=== "🏠 Listing Builder"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()

    # Create listing builder using dedicated method
    listing_id: str = client.transaction_builder.create_listing_builder()

    # Configure listing-specific details (use camelCase)
    seller_data: Dict[str, Any] = {
        "firstName": "Jane",      # Use camelCase
        "lastName": "Smith",      # Use camelCase
        "email": "jane.smith@email.com",
        "phoneNumber": "(555) 987-6543"  # Use camelCase
    }
    client.transaction_builder.add_seller(listing_id, seller_data)
    ```

=== "🔄 Convert Listing"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()

    # Convert existing listing to transaction
    listing_id: str = "existing-listing-id"
    response: Dict[str, Any] = client.transaction_builder.convert_listing_to_transaction(listing_id)
    transaction_id: str = response['id']
    print(f"Converted listing {listing_id} to transaction {transaction_id}")
    ```

---

## Core Transaction Management

### Create Transaction Builder

::: rezen.transaction_builder.TransactionBuilderClient.create_transaction_builder
    options:
      show_source: false
      heading_level: 4

!!! note "Consistent Response Format"
    The method now returns a consistent `{"id": "transaction_id"}` format instead of a raw string.

### Create Listing Builder

::: rezen.transaction_builder.TransactionBuilderClient.create_listing_builder
    options:
      show_source: false
      heading_level: 4

!!! tip "Convenience Method"
    This is a wrapper around `create_transaction_builder(builder_type='LISTING')` for easier listing creation.

### Convert Listing to Transaction

::: rezen.transaction_builder.TransactionBuilderClient.convert_listing_to_transaction
    options:
      show_source: false
      heading_level: 4

!!! example "Create Different Builder Types"

    === "Transaction Builder"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()

        # Standard transaction builder
        response: Dict[str, Any] = client.transaction_builder.create_transaction_builder()
        print(f"Transaction ID: {response['id']}")
        ```

    === "Listing Builder"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()

        # Using dedicated listing builder method
        response: Dict[str, Any] = client.transaction_builder.create_listing_builder()
        print(f"Listing ID: {response['id']}")
        ```

    === "Convert Existing Listing"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()

        # Convert listing to transaction
        listing_id = "existing-listing-id"
        response: Dict[str, Any] = client.transaction_builder.convert_listing_to_transaction(listing_id)
        print(f"New transaction ID: {response['id']}")
        ```

### Get Transaction Builder

::: rezen.transaction_builder.TransactionBuilderClient.get_transaction_builder
    options:
      show_source: false
      heading_level: 4

!!! tip "Response Structure"

    The transaction builder response includes:

    - **Basic Information**: ID, type, status, creation date
    - **Participants**: All buyers, sellers, agents, and other participants
    - **Property Details**: Location, pricing, and property information
    - **Financial Data**: Commission splits and payment information

### Submit Transaction

::: rezen.transaction_builder.TransactionBuilderClient.submit_transaction
    options:
      show_source: false
      heading_level: 4

!!! warning "Submission Requirements"

    Before submitting, ensure:

    - [ ] At least one participant is added
    - [ ] Property location is specified
    - [ ] Required financial information is complete
    - [ ] All mandatory fields are populated

### Delete Transaction Builder

::: rezen.transaction_builder.TransactionBuilderClient.delete_transaction_builder
    options:
      show_source: false
      heading_level: 4

!!! danger "Deletion Warning"

    This operation is irreversible. Ensure you have backups of any critical data before deletion.

---

## Participant Management

### Buyers

=== "➕👤 Add Buyer"

    ::: rezen.transaction_builder.TransactionBuilderClient.add_buyer
        options:
          show_source: false
          heading_level: 5

    **Required Buyer Fields:**

    | Field | Type | Description |
    |-------|------|-------------|
    | `firstName` | `str` | Buyer's first name (camelCase) |
    | `lastName` | `str` | Buyer's last name (camelCase) |
    | `email` | `str` | Valid email address |

    **Optional Buyer Fields:**

    | Field | Type | Description |
    |-------|------|-------------|
    | `phoneNumber` | `str` | Phone number (camelCase) |
    | `company` | `str` | Company name |
    | `address` | `str` | Mailing address |

    !!! example "Complete Buyer Example"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        buyer_data: Dict[str, Any] = {
            "firstName": "John",  # Use camelCase
            "lastName": "Doe",  # Use camelCase
            "email": "john.doe@email.com",
            "phoneNumber": "+1-555-123-4567",  # Use camelCase
            "company": "Doe Enterprises",
            "address": "456 Business Ave, Business City, BC 12345"
        }

        # Using new method name
        response: Dict[str, Any] = client.transaction_builder.add_buyer(transaction_id, buyer_data)
        
        # Or using backward compatibility alias
        response: Dict[str, Any] = client.transaction_builder.put_buyer_to_draft(transaction_id, buyer_data)
        ```

### Sellers

=== "➖👤 Add Seller"

    ::: rezen.transaction_builder.TransactionBuilderClient.add_seller
        options:
          show_source: false
          heading_level: 5

    !!! example "Seller Configuration"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        seller_data: Dict[str, Any] = {
            "firstName": "Jane",  # Use camelCase
            "lastName": "Smith",  # Use camelCase
            "email": "jane.smith@email.com",
            "phoneNumber": "+1-555-987-6543"  # Use camelCase
        }

        # Using new method name
        response: Dict[str, Any] = client.transaction_builder.add_seller(transaction_id, seller_data)
        
        # Or using backward compatibility alias
        response: Dict[str, Any] = client.transaction_builder.put_seller_to_draft(transaction_id, seller_data)
        ```

### Agents & Co-Agents

=== "👔 Add Co-Agent"

    ::: rezen.transaction_builder.TransactionBuilderClient.add_co_agent
        options:
          show_source: false
          heading_level: 5

    **Agent Roles:**

    !!! info "Available Agent Roles"

        - `BUYERS_AGENT`: Represents the buyer
        - `SELLERS_AGENT`: Represents the seller
        - `LISTING_AGENT`: Lists the property
        - `DUAL_AGENT`: Represents both parties

    !!! example "Co-Agent Examples"

        === "Buyer's Agent"

            ```python
            from typing import Dict, Any

            from rezen import RezenClient

            client: RezenClient = RezenClient()
            transaction_id: str = "your-transaction-id-here"

            co_agent_data: Dict[str, Any] = {
                "agent_id": "agent-uuid-here",
                "role": "BUYERS_AGENT"
            }
            client.transaction_builder.add_co_agent(transaction_id, co_agent_data)
            ```

        === "Seller's Agent"

            ```python
            from typing import Dict, Any

            from rezen import RezenClient

            client: RezenClient = RezenClient()
            transaction_id: str = "your-transaction-id-here"

            co_agent_data: Dict[str, Any] = {
                "agent_id": "seller-agent-uuid",
                "role": "SELLERS_AGENT"
            }
            client.transaction_builder.add_co_agent(transaction_id, co_agent_data)
            ```

### Owner Agents

=== "⭐👤 Update Owner Agent"

    ::: rezen.transaction_builder.TransactionBuilderClient.update_owner_agent_info
        options:
          show_source: false
          heading_level: 5

### Multiple Teams Support

!!! success "✅ New Feature: Multiple Teams Support"

    Many ReZEN users belong to multiple teams. These convenience methods help handle team selection automatically:

=== "👥 Get Teams & Offices"

    ::: rezen.transaction_builder.TransactionBuilderClient.get_user_teams_and_offices
        options:
          show_source: false
          heading_level: 5

    **Smart Default Logic:**
    - Prefers teams where you have **LEADER** role
    - Falls back to **ADMIN** teams
    - Uses first available team as last resort

=== "⭐👤 Set Owner Agent (Default Team)"

    ::: rezen.transaction_builder.TransactionBuilderClient.set_current_user_as_owner_agent
        options:
          show_source: false
          heading_level: 5

    **Best for:** Users with single team or who want automatic team selection.

=== "✅👤 Set Owner Agent (Specific Team)"

    ::: rezen.transaction_builder.TransactionBuilderClient.set_current_user_as_owner_agent_with_team
        options:
          show_source: false
          heading_level: 5

    **Best for:** Users with multiple teams who need explicit control.

    !!! danger "Prerequisites Required"

        **CRITICAL**: The owner agent endpoint requires the transaction to be properly set up BEFORE adding agents:

        1. **Location info** must be added first (`update_location_info`)
        2. **Price and date info** must be added second (`update_price_and_date_info`) 
        3. **Buyers/Sellers** must be added third (`add_buyer`/`add_seller`)
        4. **THEN** owner agent can be added successfully

    **Owner Data Structure:**
    ```python
    {
        "ownerAgent": {
            "agentId": "agent_uuid",
            "role": "BUYERS_AGENT"  # or "SELLERS_AGENT"
        },
        "officeId": "office_uuid", 
        "teamId": "team_uuid"
    }
    ```

    !!! tip "Multiple Teams Support"

        **New in ReZEN**: If you belong to multiple teams, use the enhanced methods:
        
        - `get_user_teams_and_offices()` - Discover available teams
        - `set_current_user_as_owner_agent_with_team()` - Specify exact team
        
        See [Multiple Teams Guide](../guides/transactions.md#handling-multiple-teams-offices) for details.

    !!! example "Complete Working Example"

        === "Manual Owner Agent"

            ```python
            from typing import Dict, Any

            from rezen import RezenClient

            client: RezenClient = RezenClient()

            # Step 1: Create transaction
            builder_id = client.transaction_builder.create_transaction_builder()

            # Step 2: Add location (REQUIRED FIRST)
            location_data: Dict[str, Any] = {
                "street": "123 Main St",
                "city": "Salt Lake City", 
                "state": "UTAH",
                "zip": "84101"
            }
            client.transaction_builder.update_location_info(builder_id, location_data)

            # Step 3: Add price/date info (REQUIRED SECOND)
            price_data: Dict[str, Any] = {
                "dealType": "COMPENSATING",
                "propertyType": "RESIDENTIAL", 
                "salePrice": {"amount": 500000, "currency": "USD"},
                "representationType": "BUYER"  # Must match agent role
            }
            client.transaction_builder.update_price_and_date_info(builder_id, price_data)

            # Step 4: Add clients (REQUIRED THIRD)
            client.transaction_builder.add_buyer(builder_id, {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john@example.com",
                "phoneNumber": "(801) 555-1234"
            })

            # Step 5: NOW add owner agent (will work!)
            owner_data: Dict[str, Any] = {
                "ownerAgent": {
                    "agentId": "your_agent_id",
                    "role": "BUYERS_AGENT"  # Must match representationType
                },
                "officeId": "your_office_id",
                "teamId": "your_team_id"
            }
            client.transaction_builder.update_owner_agent_info(builder_id, owner_data)
            ```

        === "Current User as Owner"

            ```python
            from typing import Dict, Any

            from rezen import RezenClient

            client: RezenClient = RezenClient()

            # Set up transaction (same steps 1-4 as above)
            builder_id = client.transaction_builder.create_transaction_builder()
            # ... add location, price, and clients ...

            # Use convenience method for current user
            client.transaction_builder.set_current_user_as_owner_agent(
                builder_id, 
                role="BUYERS_AGENT"
            )
            ```

    !!! warning "Role Matching"
        
        The `role` in `ownerAgent` must match the `representationType` in the price/date info:
        
        - `representationType: "BUYER"` → `role: "BUYERS_AGENT"`
        - `representationType: "SELLER"` → `role: "SELLERS_AGENT"`

### Other Participants

=== "👥 Add Participant"

    ::: rezen.transaction_builder.TransactionBuilderClient.add_participant
        options:
          show_source: false
          heading_level: 5

    **Participant Types:**

    | Type | Description |
    |------|-------------|
    | `INSPECTOR` | Property inspector |
    | `APPRAISER` | Property appraiser |
    | `LENDER` | Mortgage lender |
    | `TITLE_COMPANY` | Title company representative |
    | `ATTORNEY` | Legal counsel |
    | `CONTRACTOR` | Contractor or repair specialist |

    !!! example "Service Provider Examples"

        === "Property Inspector"

            ```python
            from typing import Dict, Any

            from rezen import RezenClient

            client: RezenClient = RezenClient()
            transaction_id: str = "your-transaction-id-here"

            inspector_data: Dict[str, Any] = {
                "type": "INSPECTOR",
                "firstName": "Mike",  # Use camelCase
                "lastName": "Inspector",  # Use camelCase
                "company": "Quality Inspections Inc",
                "phoneNumber": "+1-555-INSPECT",  # Use camelCase
                "email": "mike@qualityinspections.com"
            }
            client.transaction_builder.add_participant(transaction_id, inspector_data)
            ```

        === "Mortgage Lender"

            ```python
            from typing import Dict, Any

            from rezen import RezenClient

            client: RezenClient = RezenClient()
            transaction_id: str = "your-transaction-id-here"

            lender_data: Dict[str, Any] = {
                "type": "LENDER",
                "firstName": "Sarah",  # Use camelCase
                "lastName": "Banker",  # Use camelCase
                "company": "First National Bank",
                "phoneNumber": "+1-555-LOANS",  # Use camelCase
                "email": "sarah.banker@firstnational.com"
            }
            client.transaction_builder.add_participant(transaction_id, lender_data)
            ```

---

## Property & Location Details

### Location Information

::: rezen.transaction_builder.TransactionBuilderClient.update_location_info
    options:
      show_source: false
      heading_level: 4

!!! note "Backward Compatibility"
    You can also use `put_location_to_draft()` which is an alias for `update_location_info()`.

!!! example "Property Location Examples"

    === "Residential Property"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        location_data: Dict[str, Any] = {
            "street": "123 Maple Street",  # Use 'street' not 'address'
            "street2": "",
            "city": "Springfield",
            "state": "UTAH",  # Must be UTAH (all caps)
            "zip": "84101",  # Use 'zip' not 'zipCode'
            "county": "Salt Lake",
            "unit": "Unit 2A",  # For condos/apartments
            "subdivision": "Maple Grove",
            "yearBuilt": 2020,  # Use camelCase
            "mlsNumber": "MLS123",  # Use camelCase
            "escrowNumber": ""
        }
        
        # Using new method name
        client.transaction_builder.update_location_info(transaction_id, location_data)
        
        # Or using backward compatibility alias
        client.transaction_builder.put_location_to_draft(transaction_id, location_data)
        ```

    === "Commercial Property"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        location_data: Dict[str, Any] = {
            "street": "456 Business Blvd",  # Use 'street' not 'address'
            "street2": "",
            "city": "Commerce City",
            "state": "UTAH",  # Must be UTAH (all caps)
            "zip": "84111",  # Use 'zip' not 'zipCode'
            "county": "Salt Lake",
            "yearBuilt": 2018,
            "mlsNumber": "COM456",
            "escrowNumber": "",
            "building_name": "Commerce Center",
            "floor": "15th Floor"
        }
        client.transaction_builder.update_location_info(transaction_id, location_data)
        ```

### Pricing & Dates

::: rezen.transaction_builder.TransactionBuilderClient.update_price_and_date_info
    options:
      show_source: false
      heading_level: 4

!!! note "Backward Compatibility"
    You can also use `put_price_and_date_to_draft()` which is an alias for `update_price_and_date_info()`.

**Key Date Fields:**

| Field | Format | Description |
|-------|--------|-------------|
| `contractDate` | `YYYY-MM-DD` | Date contract was signed (camelCase) |
| `closingDate` | `YYYY-MM-DD` | Expected closing date (camelCase) |
| `inspectionDate` | `YYYY-MM-DD` | Property inspection date (camelCase) |
| `appraisalDate` | `YYYY-MM-DD` | Appraisal completion date (camelCase) |
| `acceptanceDate` | `YYYY-MM-DD` | Offer acceptance date (camelCase) |

!!! example "Pricing Information"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()
    transaction_id: str = "your-transaction-id-here"

    price_date_data: Dict[str, Any] = {
        "salePrice": {  # Use camelCase and object structure
            "amount": 750000,
            "currency": "USD"
        },
        "earnestMoney": 15000,  # Use camelCase
        "downPayment": 150000,  # Use camelCase
        "loanAmount": 600000,  # Use camelCase
        "contractDate": "2024-02-01",  # Use camelCase
        "closingDate": "2024-03-15",  # Use camelCase
        "inspectionDate": "2024-02-10",  # Use camelCase
        "appraisalDate": "2024-02-20"  # Use camelCase
    }

    client.transaction_builder.update_price_and_date_info(
        transaction_id,
        price_date_data
    )
    ```

### Title Information

::: rezen.transaction_builder.TransactionBuilderClient.update_title_info
    options:
      show_source: false
      heading_level: 4

### Update Real Title

::: rezen.transaction_builder.TransactionBuilderClient.update_real_title
    options:
      show_source: false
      heading_level: 4

!!! tip "Alias Method"
    This is an alias for `update_title_info()` provided for backward compatibility.

!!! example "Title Company Details"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()
    transaction_id: str = "your-transaction-id-here"

    title_data: Dict[str, Any] = {
        "company": "Premier Title Co",  # Use 'company' not 'title_company'
        "firstName": "Sarah",  # Use camelCase
        "lastName": "Johnson",  # Use camelCase
        "phoneNumber": "+1-555-789-0123",  # Use camelCase
        "email": "sarah@premiertitle.com",
        "address": "789 Title Lane, Title City, TC 54321",
        "policyNumber": "PT-2024-001234"  # Use camelCase
    }

    # Using either method works the same
    client.transaction_builder.update_title_info(transaction_id, title_data)
    # or
    client.transaction_builder.update_real_title(transaction_id, title_data)
    ```

### Personal Deal Information

::: rezen.transaction_builder.TransactionBuilderClient.update_personal_deal_info
    options:
      show_source: false
      heading_level: 4

### Update Personal Deal

::: rezen.transaction_builder.TransactionBuilderClient.update_personal_deal
    options:
      show_source: false
      heading_level: 4

!!! tip "Alias Method"
    This is an alias for `update_personal_deal_info()` provided for backward compatibility.

---

## Financial Management

### Commission Splits

::: rezen.transaction_builder.TransactionBuilderClient.update_commission_splits
    options:
      show_source: false
      heading_level: 4

!!! example "Commission Split Examples"

    === "Equal Split"

        ```python
        from typing import Dict, List, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        commission_data: List[Dict[str, Any]] = [
            {
                "agentId": "buyer-agent-uuid",  # Use camelCase
                "splitPercentage": 50.0,  # Use camelCase
                "commissionAmount": 15000  # Use camelCase
            },
            {
                "agentId": "seller-agent-uuid",  # Use camelCase
                "splitPercentage": 50.0,  # Use camelCase
                "commissionAmount": 15000  # Use camelCase
            }
        ]

        client.transaction_builder.update_commission_splits(
            transaction_id,
            commission_data
        )
        ```

    === "Unequal Split"

        ```python
        from typing import Dict, List, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        commission_data: List[Dict[str, Any]] = [
            {
                "agentId": "listing-agent-uuid",  # Use camelCase
                "splitPercentage": 60.0,  # Use camelCase
                "commissionAmount": 18000  # Use camelCase
            },
            {
                "agentId": "buyer-agent-uuid",  # Use camelCase
                "splitPercentage": 40.0,  # Use camelCase
                "commissionAmount": 12000  # Use camelCase
            }
        ]

        client.transaction_builder.update_commission_splits(
            transaction_id,
            commission_data
        )
        ```

### Commission Payers

::: rezen.transaction_builder.TransactionBuilderClient.add_commission_payer
    options:
      show_source: false
      heading_level: 4

### Update Commission Payer

::: rezen.transaction_builder.TransactionBuilderClient.update_commission_payer
    options:
      show_source: false
      heading_level: 4

!!! tip "Alias Method"
    This is an alias for `add_commission_payer()` provided for backward compatibility.

**Payer Types:**

| Type | Description |
|------|-------------|
| `SELLER` | Seller pays commission |
| `BUYER` | Buyer pays commission |
| `BOTH` | Split between buyer and seller |

!!! example "Commission Payer Configuration"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()
    transaction_id: str = "your-transaction-id-here"

    payer_data: Dict[str, Any] = {
        "payerType": "SELLER",  # Use camelCase
        "commissionRate": 6.0,  # 6% commission, use camelCase
        "flatFee": False  # Percentage-based, not flat fee, use camelCase
    }

    # Using either method works the same
    client.transaction_builder.add_commission_payer(transaction_id, payer_data)
    # or
    client.transaction_builder.update_commission_payer(transaction_id, payer_data)
    ```

---

## Field Name Requirements

!!! danger "Critical Field Name Requirements"

    The ReZEN API has specific field name requirements that must be followed exactly:

    **Location Fields:**
    - ✅ Use `street` NOT `address`
    - ✅ Use `zip` NOT `zipCode`
    - ✅ State must be `UTAH` (all caps)
    - ✅ Use camelCase: `yearBuilt`, `mlsNumber`, `escrowNumber`

    **Contact Fields:**
    - ✅ Use `firstName` NOT `first_name`
    - ✅ Use `lastName` NOT `last_name`
    - ✅ Use `phoneNumber` NOT `phone`

    **Price Fields:**
    - ✅ `salePrice` must be an object with `amount` and `currency`
    - ✅ Use camelCase: `earnestMoney`, `downPayment`, `loanAmount`

    **Date Fields:**
    - ✅ Use camelCase: `contractDate`, `closingDate`, `acceptanceDate`
    - ✅ Format: `YYYY-MM-DD`

    **Commission Fields:**
    - ✅ Use camelCase: `agentId`, `splitPercentage`, `commissionAmount`

---

## Backward Compatibility

!!! info "Legacy Method Names"
    
    The library provides backward compatibility aliases for users migrating from older versions:
    
    | Old Method Name | New Method Name |
    |----------------|-----------------|
    | `put_buyer_to_draft()` | `add_buyer()` |
    | `put_seller_to_draft()` | `add_seller()` |
    | `put_location_to_draft()` | `update_location_info()` |
    | `put_price_and_date_to_draft()` | `update_price_and_date_info()` |
    | `update_commission_payer()` | `add_commission_payer()` |
    | `update_personal_deal()` | `update_personal_deal_info()` |
    | `update_real_title()` | `update_title_info()` |

!!! example "Using Backward Compatibility"

    ```python
    from rezen import RezenClient

    client = RezenClient()
    transaction_id = "your-transaction-id"

    # These method pairs do the same thing:
    
    # Add buyer
    client.transaction_builder.add_buyer(transaction_id, buyer_data)
    client.transaction_builder.put_buyer_to_draft(transaction_id, buyer_data)
    
    # Add seller
    client.transaction_builder.add_seller(transaction_id, seller_data)
    client.transaction_builder.put_seller_to_draft(transaction_id, seller_data)
    
    # Update location
    client.transaction_builder.update_location_info(transaction_id, location_data)
    client.transaction_builder.put_location_to_draft(transaction_id, location_data)
    
    # Update price and date
    client.transaction_builder.update_price_and_date_info(transaction_id, price_data)
    client.transaction_builder.put_price_and_date_to_draft(transaction_id, price_data)
    ```

---

## Query & Search Operations

### List Transaction Builders

::: rezen.transaction_builder.TransactionBuilderClient.get_transaction_builders
    options:
      show_source: false
      heading_level: 4

!!! example "Advanced Filtering"

    === "Basic Pagination"

        ```python
        builders = client.transaction_builder.get_transaction_builders(
            limit=20,
            from_offset=0
        )

        print(f"Found {len(builders)} transaction builders")
        for builder in builders:
            print(f"ID: {builder['id']}, Status: {builder['status']}")
        ```

    === "User-Specific Search"

        ```python
        # Get builders for specific user
        user_builders = client.transaction_builder.get_transaction_builders(
            limit=50,
            from_offset=0,
            yenta_id="user-uuid-here",
            builder_type="TRANSACTION"
        )
        ```

    === "Listing Builders Only"

        ```python
        # Get only listing builders
        listings = client.transaction_builder.get_transaction_builders(
            limit=25,
            from_offset=0,
            builder_type="LISTING"
        )
        ```

---

## Error Handling

### Enhanced Error Messages

The Transaction Builder now includes enhanced error handling that catches common mistakes before they reach the API.

!!! success "New Error Types"

    - **`InvalidFieldNameError`**: Catches incorrect field names (e.g., `address` instead of `street`)
    - **`InvalidFieldValueError`**: Validates field formats (e.g., state must be uppercase)
    - **`TransactionSequenceError`**: Identifies when operations are called in wrong order
    - **`ValidationError`**: General validation failures with detailed messages

### Common Field Name Errors

!!! example "Field Name Validation"

    ```python
    from rezen.exceptions import InvalidFieldNameError

    try:
        # Using wrong field name
        location_data = {
            "address": "123 Main St",  # ❌ Wrong! Should be 'street'
            "city": "Salt Lake City",
            "state": "UTAH",
            "zipCode": "84101"  # ❌ Wrong! Should be 'zip'
        }
        client.transaction_builder.update_location_info(transaction_id, location_data)
    except InvalidFieldNameError as e:
        print(f"Field name error: {e}")
        print(f"Use '{e.correct_name}' instead of '{e.field_name}'")
    ```

### Field Value Validation

!!! example "Field Value Validation"

    ```python
    from rezen.exceptions import InvalidFieldValueError

    try:
        # Wrong state format
        location_data = {
            "street": "123 Main St",
            "city": "Salt Lake City",
            "state": "utah",  # ❌ Wrong! Must be uppercase
            "zip": "84101"
        }
        client.transaction_builder.update_location_info(transaction_id, location_data)
    except InvalidFieldValueError as e:
        print(f"Invalid value for '{e.field_name}': {e.value}")
        print(f"Expected: {e.expected_format}")
    ```

### Transaction Sequence Errors

!!! danger "Sequence Requirements"

    The owner agent endpoint requires specific setup steps in order:

    ```python
    from rezen.exceptions import TransactionSequenceError

    try:
        # Trying to add owner agent without proper setup
        client.transaction_builder.update_owner_agent_info(builder_id, owner_data)
    except TransactionSequenceError as e:
        print(f"Sequence error: {e}")
        # Error message includes required steps:
        # 1. Create transaction (create_transaction_builder)
        # 2. Add location info (update_location_info) - REQUIRED FIRST
        # 3. Add price/date info (update_price_and_date_info) - REQUIRED SECOND
        # 4. Add buyers/sellers (add_buyer/add_seller) - REQUIRED THIRD
        # 5. THEN add owner agent (update_owner_agent_info)
    ```

### Price Structure Validation

!!! example "Price Field Validation"

    ```python
    from rezen.exceptions import InvalidFieldValueError, ValidationError

    try:
        price_data = {
            "dealType": "COMPENSATING",
            "propertyType": "RESIDENTIAL",
            "salePrice": 500000,  # ❌ Wrong! Must be object
            "representationType": "BUYERS_AGENT"  # ❌ Wrong! Should be 'BUYER'
        }
        client.transaction_builder.update_price_and_date_info(transaction_id, price_data)
    except InvalidFieldValueError as e:
        # Catches: "Invalid value for 'salePrice': 500000. 
        # Expected: Object with 'amount' and 'currency' fields"
        print(f"Error: {e}")
    except ValidationError as e:
        # Catches missing required fields
        print(f"Validation error: {e}")
    ```

### Best Practices

!!! info "Error Handling Best Practices"

    - **Catch Specific Exceptions**: Use specific exception types for better error handling
    - **Check Field Names**: The enhanced validation catches common camelCase vs snake_case errors
    - **Validate Before Submission**: Required fields are now validated before API calls
    - **Follow Sequence Requirements**: Especially important for owner agent endpoints
    - **Use Error Details**: Exception objects contain helpful properties like `field_name` and `correct_name`

---

## Complete Workflow Example

!!! example "End-to-End Transaction Creation"

    ```python
    from rezen import RezenClient
    from rezen.exceptions import RezenError
    import logging

    def create_complete_transaction():
        """Create a complete transaction with all participants and details."""

        try:
            client = RezenClient()

            # Step 1: Create transaction builder
            print("Creating transaction builder...")
            response = client.transaction_builder.create_transaction_builder()
            transaction_id = response['id']
            print(f"✅ Created transaction: {transaction_id}")

            # Step 2: Add buyer
            print("Adding buyer...")
            buyer_data = {
                "firstName": "John",  # Use camelCase
                "lastName": "Doe",  # Use camelCase
                "email": "john.doe@email.com",
                "phoneNumber": "+1-555-123-4567"  # Use camelCase
            }
            client.transaction_builder.add_buyer(transaction_id, buyer_data)
            print("✅ Added buyer")

            # Step 3: Add seller
            print("Adding seller...")
            seller_data = {
                "firstName": "Jane",  # Use camelCase
                "lastName": "Smith",  # Use camelCase
                "email": "jane.smith@email.com",
                "phoneNumber": "+1-555-987-6543"  # Use camelCase
            }
            client.transaction_builder.add_seller(transaction_id, seller_data)
            print("✅ Added seller")

            # Step 4: Add property location
            print("Setting property location...")
            location_data = {
                "street": "123 Dream House Lane",  # Use 'street' not 'address'
                "street2": "",
                "city": "Salt Lake City",
                "state": "UTAH",  # Must be UTAH (all caps)
                "zip": "84101",  # Use 'zip' not 'zipCode'
                "county": "Salt Lake",
                "unit": "",
                "yearBuilt": 2020,  # Use camelCase
                "mlsNumber": "MLS123456",  # Use camelCase
                "escrowNumber": ""
            }
            client.transaction_builder.update_location_info(transaction_id, location_data)
            print("✅ Set property location")

            # Step 5: Set pricing and dates
            print("Setting pricing and dates...")
            price_data = {
                "salePrice": {  # Use camelCase and object structure
                    "amount": 850000,
                    "currency": "USD"
                },
                "earnestMoney": 17000,  # Use camelCase
                "acceptanceDate": "2024-02-01",  # Use camelCase
                "closingDate": "2024-03-15"  # Use camelCase
            }
            client.transaction_builder.update_price_and_date_info(transaction_id, price_data)
            print("✅ Set pricing and dates")

            # Step 6: Add service providers
            print("Adding service providers...")
            inspector_data = {
                "type": "INSPECTOR",
                "firstName": "Mike",  # Use camelCase
                "lastName": "Inspector",  # Use camelCase
                "company": "Quality Inspections Inc",
                "phoneNumber": "+1-555-INSPECT",  # Use camelCase
                "email": "mike@qualityinspections.com"
            }
            client.transaction_builder.add_participant(transaction_id, inspector_data)
            print("✅ Added inspector")

            # Step 7: Submit transaction
            print("Submitting transaction...")
            submit_response = client.transaction_builder.submit_transaction(transaction_id)
            print("✅ Transaction submitted successfully!")

            return {
                "success": True,
                "transaction_id": transaction_id,
                "submit_response": submit_response
            }

        except RezenError as e:
            logging.error(f"ReZEN API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "transaction_id": transaction_id if 'transaction_id' in locals() else None
            }
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # Run the example
    result = create_complete_transaction()
    if result["success"]:
        print(f"🎉 Transaction {result['transaction_id']} created successfully!")
    else:
        print(f"❌ Failed to create transaction: {result['error']}")
    ```

---

## Next Steps

<div class="grid cards" markdown>

-   [🤝 **Transactions API**](transactions.md)

    Work with live transactions and manage ongoing deals

-   [👥 **Teams API**](teams.md)

    Search and manage team information

-   [👔 **Agents API**](agents.md)

    Find and manage agent information

-   [📄 **Examples**](../guides/examples.md)

    See more practical usage examples

</div>
