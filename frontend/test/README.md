# UI Testing with Playwright

## Setup

1. Make sure Playwright browsers are installed:
```bash
playwright install chromium
```

2. Make sure the FastAPI server is running:
```bash
python app.py
```

The server should be running on `http://localhost:8082`

## Running the Tests

### Option 1: Using Python directly
```bash
python frontend/test/test_ui.py
```

### Option 2: Using the batch file (Windows)
```bash
run_ui_test.bat
```

### Option 3: Using pytest (recommended)
```bash
pytest frontend/test/test_ui.py -v
```

## Test Details

### test_refresh_and_filter_workflow

This test validates the filter functionality:

1. Opens the dashboard at http://localhost:8082
2. Waits for data to load
3. Clicks the refresh button
4. Opens the invoice filter dropdown
5. Unchecks "Medium" risk level (leaving only "High")
6. Applies the filter
7. Validates that:
   - The filter button shows as active (green)
   - All visible invoice rows show only "High" risk level

## Troubleshooting

### "strict mode violation" Error
This has been fixed. The issue was that multiple "Apply" buttons existed (one per filter section). The test now uses a specific selector: `#invoice-filter-dropdown button.apply-filter-btn`

### Loading Spinner Never Disappears
Make sure:
- The FastAPI server is running
- ERPNext connection is configured in `.env`
- The API endpoints are returning data (check browser console)

### Test Trace Files
After each test run, a trace file is saved to:
```
frontend/test/traces/dashboard_ui_trace.zip
```

You can view this in Playwright Trace Viewer:
```bash
playwright show-trace frontend/test/traces/dashboard_ui_trace.zip
```

## Key Fixes Applied

1. ✅ Fixed Apply button selector to be specific to invoice filters
2. ✅ Added wait for filter dropdown to be visible before interacting
3. ✅ Improved table row selector to target only invoice table
4. ✅ Added timeout for filter application
5. ✅ Fixed filter button class assertion to handle multiple classes
6. ✅ Added handling for empty results (no high risk invoices)
7. ✅ Improved wait_for_table to wait for loading to disappear
8. ✅ Auto-create traces directory if it doesn't exist
