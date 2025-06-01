# Directory Endpoints Implementation

## Vendor Endpoints
- [ ] POST /directory/vendors - Create a vendor
- [ ] GET /directory/vendors/{id} - Get vendor by id
- [ ] PATCH /directory/vendors/{id} - Update vendor by id
- [ ] GET /directory/vendors/{id}/w9 - Get vendor's W9 URL
- [ ] PATCH /directory/vendors/{id}/w9 - Update vendor's W9 file
- [ ] PATCH /directory/vendors/{id}/archive - Archive/unarchive vendor
- [ ] GET /directory/vendors/search/all - Search all vendors with filtering

## Person Endpoints
- [ ] POST /directory/persons - Create a person
- [ ] GET /directory/persons/{id} - Get person by id
- [ ] PATCH /directory/persons/{id} - Update person by id
- [ ] PATCH /directory/persons/{id}/unlink - Unlink person from vendor
- [ ] PATCH /directory/persons/{id}/link - Link person to vendor
- [ ] PATCH /directory/persons/{id}/archive - Archive/unarchive person
- [ ] GET /directory/persons/search/all - Search all persons with filtering

## General Directory Endpoints
- [ ] GET /directory/roles - Get available roles for directory entries
- [ ] GET /directory/entries/search/all - Search all directory entries (vendors + persons)

## Total: 14 endpoints 