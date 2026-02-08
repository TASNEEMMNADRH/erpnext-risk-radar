# Test Plan – Integration Tests (ERPNext Services)

## 1. Introduction
This document describes the integration test strategy for the ERPNext service layer.

The purpose of these tests is to verify:
- Correct communication with a real ERPNext environment
- Proper authentication and request headers
- Validity and structure of real ERPNext responses
- Business rules applied to ERPNext data

Unlike unit tests, these tests execute **real HTTP requests** against ERPNext.

---

## 2. Scope

### 2.1 In Scope
Integration tests for the following ERPNext service functions:

- Environment validation
  - ERP connection variables

- Authentication & Headers
  - `get_headers`

- Sales Invoices
  - `get_sales_invoices`

- Overdue Invoices
  - `get_overdue_invoices`

- Bin Stock / Inventory
  - `get_bin_stock`

- Low Stock Items
  - `get_low_stock_items`

- Delayed Purchase Orders
  - `get_delayed_purchase_orders`

The tests validate:
- Real API connectivity
- Data structure and mandatory fields
- Business logic assumptions (risk levels, thresholds)
- ERPNext response consistency

---

### 2.2 Out of Scope
- Mock-based testing
- API layer (FastAPI routes)
- UI validation
- Performance, stress, and load testing
- Data creation or mutation in ERPNext

---

## 3. Test Type & Strategy

- **Integration Tests**
- Direct communication with ERPNext REST API
- No mocking of ERPNext services
- Read-only operations only

**Technologies:**
- Test framework: `pytest`
- Language: Python
- External system: ERPNext (real environment)

---

## 4. Test Environment

| Component | Value |
|---------|------|
| Language | Python 3.x |
| Test Framework | pytest |
| ERP System | ERPNext |
| Environment | Real / Staging ERPNext |
| Network | Required |

---

## 5. Preconditions & Configuration

The following environment variables **must be defined** before running the tests:

- `ERP_URL`
- `ERP_API_KEY`
- `ERP_API_SECRET`

Tests will fail immediately if any required variable is missing.

---

## 6. Test Data Strategy

- All data is retrieved from **live ERPNext**
- No test data is inserted or modified
- Tests assume ERPNext contains:
  - Existing invoices
  - Stock records
  - Purchase orders

Assertions are intentionally flexible to account for real-world data variability.

---

## 7. Test Scenarios

### 7.1 Environment Validation
- Verify all required ERP environment variables exist
- Prevent test execution with invalid configuration

---

### 7.2 Authentication & Headers
**Function:** `get_headers`

- Validate presence of `Authorization` header
- Validate correct token format
- Validate accepted content type

---

### 7.3 Sales Invoices
**Function:** `get_sales_invoices`

**Validations:**
- Returned value is a list
- Each invoice includes:
  - `name`
  - `customer`
  - `due_date`
  - `outstanding_amount`
- Outstanding amount is non-negative

---

### 7.4 Overdue Invoices
**Function:** `get_overdue_invoices`

**Validations:**
- Response contains:
  - KPI summary
  - Data list
- Each invoice:
  - Is overdue by at least 8 days
  - Has valid risk classification (`Medium`, `High`)
  - Has positive outstanding amount

---

### 7.5 Bin Stock
**Function:** `get_bin_stock`

**Validations:**
- Response contains count and data
- Each item includes:
  - `item_code`
  - `total_qty`
  - `warehouses`
- Quantity type is numeric (negative values allowed by ERPNext)

---

### 7.6 Low Stock Items
**Function:** `get_low_stock_items`

**Validations:**
- Response contains:
  - `data`
  - `high_count`
  - `medium_count`
- Each item:
  - Belongs to an expected warehouse
  - Has valid risk level
  - Matches quantity thresholds:
    - High: `< 30`
    - Medium: `30–60`

---

### 7.7 Delayed Purchase Orders
**Function:** `get_delayed_purchase_orders`

**Validations:**
- Response contains:
  - `data`
  - `high_count`
  - `medium_count`
- Each purchase order:
  - Is delayed by at least 7 days
  - Has valid risk level

---

## 8. Entry Criteria
- ERPNext environment is accessible
- Valid API credentials are configured
- Network connectivity is available

---

## 9. Exit Criteria
- All integration tests pass
- No authentication or connectivity errors
- ERPNext responses conform to expected structures

---

## 10. Risks & Assumptions

### Risks
- ERPNext data may change between test runs
- Network or ERPNext downtime may cause failures
- Business rules in ERPNext may evolve

### Assumptions
- ERPNext API remains backward compatible
- Tests run against a non-production or safe environment
- Read-only access is sufficient

---

## 11. Summary
This test plan ensures that the ERPNext service layer:
- Communicates correctly with a real ERPNext system
- Returns valid and consistent business data
- Applies correct business rules for risk classification
