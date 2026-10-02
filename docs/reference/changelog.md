# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.1] - 2026-10-02

### Fixed

- Run package publishing, documentation deployment, and GitHub release jobs after
  a successful tag build even when the manual version-bump job is skipped. Retain
  explicit successful-build and release-mode checks, so failed builds cannot publish.

## [2.3.0] - 2026-10-02 (not published)

### Added

- `BuyerRecordsClient`, exported publicly and available as `client.buyer_records`,
  for Buyer Record creation, search, retrieval, updates, participants, conversion,
  and termination requests.
- `TransactionBuilderClient.update_associations` for Buyer Record and listing links.
- HTTP contract tests and migration documentation for Real's October 12, 2026
  buyer transaction API change. Direct listing creation remains available.

## [2.2.16] - 2026-09-26

### ✨ Added
- Add `TransactionsClient.set_payouts` for `PUT /transactions/{transactionId}/payouts` (`setPayouts`), which corrects participant payouts on an existing transaction in place without a builder resubmit
- Validate payout bodies before sending: at least one payment, a participant ID on each entry, and exactly one of `money`, `percentage` or `zero` per `paymentValue`
- Send `Decimal` payout amounts as JSON numbers, and reject `money` without `amount`, `percentage` without `value`, or `zero` that is not `True`

### 📚 Docs
- Document `set_payouts` under Transactions → Financial Operations

---

## [2.2.15] - 2025-12-30

### ✨ Added
- Add `RevShareClient` with full `rev-share-controller` coverage (payments, exports, contributors, contributions, history, performance)
- Wire revshare into `RezenClient` via `client.rev_share`
- Add comprehensive unit tests for revshare endpoints

### 📚 Docs
- Update API index to mention Rev Share support and usage

---

## [2.2.11] - 2025-08-21

### 🔐 Authentication & Multipart
- Ensure all multipart/form-data requests send `X-API-KEY` (not Authorization Bearer)
- Fix `add_participant` to send multipart form fields like Postman examples
- Add tests verifying multipart header and content-type behavior
- Update docs for `add_participant` and `add_commission_payer` to call out multipart requirements

### 🧪 Tests & Tooling
- Expand auth header tests to cover multipart scenarios

---

## [2.2.6] - 2025-01-29

### 🎯 Critical Fix
- **RESOLVED: June 2024 Listing Posting Issue** - Fixed location update validation that was causing "Bad request: Invalid request" errors when posting listings
- **Location Updates Now Work Correctly** - Added comprehensive validation and documentation for the 3 required additional fields:
  - `county` (string) - REQUIRED beyond basic address fields
  - `yearBuilt` (integer) - REQUIRED beyond basic address fields  
  - `mlsNumber` (string) - REQUIRED beyond basic address fields

### ✨ Enhanced
- **Comprehensive Field Validation** - Added helpful error messages for common field naming mistakes:
  - Use `street` not `address`
  - Use `zip` not `zipCode` or `zip_code`
  - State codes must be ALL CAPS (e.g., `UTAH`, `CALIFORNIA`)
  - Use camelCase: `yearBuilt`, `mlsNumber`, `escrowNumber`
- **Improved Documentation** - Updated all location-related examples and documentation to include required fields
- **Better Error Messages** - Validation errors now provide clear guidance on fixing field name and format issues
- **End-to-End Testing** - Added comprehensive tests covering location validation scenarios and complete listing workflows

### 🔧 Technical Details
- **Breaking Change Context**: This resolves the breaking change introduced when migrating from Tapioca-based API client to official rezen library in June 2024
- **Backward Compatibility**: All existing method names (`put_location_to_draft`, etc.) continue to work as aliases
- **API Requirements**: The ReZEN API began enforcing stricter validation requirements that were not well-documented in version 1.7.1
- **Current Support**: All validation and requirements are fully supported in version 2.2.6+

### 📋 Migration Guide
For users affected by the June 2024 listing posting issue:

**Before (Failing):**
```python
location_data = {
    "address": "123 Main Street",  # Wrong field name
    "city": "Salt Lake City",
    "state": "utah",               # Wrong case
    "zipCode": "84101"            # Wrong field name
}
```

**After (Working):**
```python
location_data = {
    "street": "123 Main Street",   # Correct field name
    "city": "Salt Lake City", 
    "state": "UTAH",              # ALL CAPS required
    "zip": "84101",               # Correct field name
    "county": "Salt Lake",        # REQUIRED - was missing
    "yearBuilt": 2020,           # REQUIRED - was missing
    "mlsNumber": "MLS123456"     # REQUIRED - was missing
}
```

## [2.2.5] - 2024-01-XX

### Fixed
- Fix dealType field value issue

## [2.2.4] - 2024-01-XX

### Fixed
- Commission payer documentation and tests

## [2.2.3] - 2024-01-XX

### Fixed
- Fix add_participant multipart/form-data bug

## [2.2.2] - 2024-01-XX

### Fixed
- Improve emoji rendering in documentation

## [2.2.1] - 2024-01-XX

### Fixed
- Simplify mkdocs emoji configuration to prevent YAML parsing errors

## [2.1.0] - 2024-01-XX

### Added
- Consolidate workflows into unified deployment
- Merge release and docs workflows

## [2.0.1] - 2024-01-XX

### Fixed
- Code formatting, linting, and version bump
- Applied Black formatting to all Python files
- Applied isort to sort imports
- Passed mypy type checking
- Rebuilt documentation with mkdocs

## [2.0.0] - 2024-01-XX

### Added
- Major version release
- Significant API improvements and stabilization

## [1.7.1] - 2024-06-XX

### Note
- This version introduced stricter location validation requirements that caused listing posting failures
- Issues resolved in version 2.2.6+

---

**Legend:**
- 🎯 Critical fixes and major improvements
- ✨ New features and enhancements  
- 🔧 Technical changes and improvements
- 📋 Migration guides and breaking changes
- 🐛 Bug fixes
