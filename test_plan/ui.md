# Test Plan – UI Tests (Dashboard Filters)

## 1. Introduction
This document describes the UI test strategy for the web dashboard application.

The purpose of these tests is to verify that:
- The dashboard loads correctly
- UI filters behave as expected
- User interactions result in correct data presentation
- The application remains stable in both local and CI environments

Tests are implemented using Playwright with a Page Object Model (POM) design.

---

## 2. Scope

### 2.1 In Scope
UI tests covering the dashboard page:

- Dashboard loading and refresh behavior
- Invoice filters:
  - Risk level
  - Customer
  - Amount range
  - Days overdue range
  - Combined filters

- Stock filters:
  - Warehouse
  - Quantity range
  - Risk level
  - Combined filters

The tests validate:
- UI element visibility and interaction
- Filter activation state
- Correct filtering of table rows
- Consistency between filter inputs and displayed results

---

### 2.2 Out of Scope
- Backend API logic
- ERPNext integration logic
- Data accuracy validation against backend
- Performance and load testing
- Cross-browser testing (non-Chromium)

---

## 3. Test Type & Strategy

- **End-to-End UI Tests**
- **Black-box testing from a user perspective**
- Page Object Model (POM) for maintainability
- Real browser automation

**Technologies:**
- Test framework: `unittest`
- UI automation: Playwright (sync API)
- Browser: Chromium
- Design pattern: Page Object Model (POM)

---

## 4. Test Environment

| Component | Value |
|---------|------|
| Language | Python 3.x |
| UI Framework | Web Dashboard |
| Automation Tool | Playwright |
| Browser | Chromium |
| Execution Mode | Headed (local) / Headless (CI) |

The base URL is configurable using the `BASE_URL` environment variable.

---

## 5. Preconditions & Configuration

- Application is accessible via browser
- Dashboard page is reachable at `/static/dashboard.html`
- Required environment variables:
  - `BASE_URL`
  - `CI` (optional)
  - `HEADLESS` (local execution)

CI execution always runs in **headless mode**.

---

## 6. Test Data Strategy

- Tests rely on existing dashboard data
- No test data is created or modified
- Assertions are tolerant to data variability
- Filters are validated based on UI behavior, not exact record counts

---

## 7. Test Scenarios

### 7.1 Dashboard Load & Refresh
- Verify dashboard page loads successfully
- Verify invoice table is rendered
- Verify refresh button reloads data correctly
- Capture screenshot and HTML on load failure (CI support)

---

### 7.2 Invoice Filters

**Scenarios:**
- Filter by high risk invoices only
- Filter by customer
- Filter by invoice amount range
- Filter by overdue days range
- Apply all invoice filters simultaneously

**Validations:**
- Filter button reflects active state
- Table rows match selected risk level
- Filtered results are consistent
- Combined filters reduce or maintain result count

---

### 7.3 Stock Filters

**Scenarios:**
- Filter stock by warehouse
- Filter stock by quantity range
- Filter stock by medium risk only
- Filter stock by warehouse and quantity

**Validations:**
- All rows match selected warehouse
- Quantities fall within specified range
- Risk badges reflect selected risk level

---

## 8. Entry Criteria
- Application is running and accessible
- Browser automation environment is available
- Required environment variables are configured

---

## 9. Exit Criteria
- All UI tests pass successfully
- Dashboard loads without UI errors
- Filters behave consistently across scenarios

---

## 10. Risks & Assumptions

### Risks
- UI changes may break selectors
- Dynamic data may cause result variability
- CI environment may be slower than local

### Assumptions
- Dashboard structure and element IDs remain stable
- Filters operate purely on client-side or API responses
- Chromium browser behavior is consistent across environments

---

## 11. Summary
This test plan ensures that the dashboard UI:
- Is usable and stable
- Correctly reflects user-selected filters
- Provides consistent behavior in both local and CI environments

The use of Playwright and POM improves test reliability, readability, and maintainability.
