# Test Plan – API Layer (ERPNext Integration)

## 1. Introduction
This document describes the test strategy and test cases for the FastAPI backend
that exposes ERPNext-related endpoints.  
The goal is to verify correctness, stability, and error handling of the API layer
independently from the ERPNext system.

---

## 2. Scope

### In Scope
The following API endpoints are covered by automated tests:

- Health & root endpoints
  - `GET /health`
  - `GET /` (redirect)

- Sales Invoices
  - `GET /invoices`

- Overdue Invoices
  - `GET /invoices/overdue`

- Stock Ledger
  - `GET /stock-ledger`

- Low Stock Inventory
  - `GET /inventory/low-stock`

- Delayed Purchase Orders
  - `GET /purchase-orders/delayed`

The tests validate:
- HTTP status codes
- Response structure and fields
- Default and custom query parameters
- Error mapping from ERPNext to API responses

---

### Out of Scope
- Real ERPNext API calls
- Database persistence
- Performance and load testing
- Frontend / UI validation

---

## 3. Test Type

- **API Tests**
- **Integration-like tests with mocked services**
- Framework: `unittest`
- HTTP client: `FastAPI TestClient`
- Mocking: `unittest.mock`
- External dependency isolation via mocks (ERPNext services)

---

## 4. Test Environment

| Component | Value |
|---------|------|
| Language | Python 3.x |
| Framework | FastAPI |
| Test Runner | unittest |
| HTTP Client | TestClient |
| External API | ERPNext (mocked) |

No external services are required to execute the tests.

---

## 5. Test Data Strategy

- All test data is **synthetic**
- ERPNext service functions are mocked:
  - `get_sales_invoices`
  - `get_overdue_invoices`
  - `get_bin_stock`
  - `get_low_stock_items`
  - `get_delayed_purchase_orders`

This ensures:
- Deterministic results
- No dependency on network or credentials

---

## 6. Test Scenarios

### 6.1 Health & Root
- Verify API health endpoint returns `200 OK`
- Verify root endpoint redirects to dashboard

---

### 6.2 Sales Invoices (`/invoices`)
**Positive cases**
- Valid request with limit parameter
- Default limit when not provided

**Error handling**
- `ValueError` → `500 Internal Server Error`
- `HTTPError 401` → `401 Unauthorized`
- `HTTPError != 401` → `502 Bad Gateway`
- `ConnectionError` → `502 Bad Gateway`

---

### 6.3 Overdue Invoices (`/invoices/overdue`)
**Positive cases**
- Valid response with risk categorization
- Correct aggregation fields (`count`, `medium_count`, `high_count`)

**Error handling**
- Same mapping strategy as sales invoices

---

### 6.4 Stock Ledger (`/stock-ledger`)
**Positive cases**
- Aggregated stock per item
- Warehouse breakdown validation
- Correct query parameter forwarding

**Error handling**
- `ValueError` → `500`
- `HTTPError 401` → `401`
- `HTTPError != 401` → `502`
- `ConnectionError` → `502`

---

### 6.5 Low Stock Inventory (`/inventory/low-stock`)
**Positive cases**
- Retrieve low stock items
- Filter by `warehouse`
- Filter by `item_code`

**Error handling**
- Consistent ERPNext error mapping

---

### 6.6 Delayed Purchase Orders (`/purchase-orders/delayed`)
**Positive cases**
- Custom limit
- Default limit behavior

**Error handling**
- ERPNext authentication failure
- ERPNext service failure
- Network connectivity issues

---

## 7. Entry Criteria
- Application loads successfully
- FastAPI app instance is importable
- Test environment is isolated (no real ERPNext calls)

---

## 8. Exit Criteria
- All tests pass successfully
- No unhandled exceptions
- API error mapping behaves as expected

---

## 9. Risks & Assumptions

### Risks
- ERPNext API behavior may change
- Error messages may differ in real environments

### Assumptions
- ERPNext service layer raises standard `requests` exceptions
- API layer is responsible for error translation

---

## 10. Summary
This test plan ensures that the API layer:
- Correctly exposes ERPNext data
- Handles errors gracefully
- Remains stable and testable without external dependencies
