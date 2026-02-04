import os
import pytest
from datetime import date

from services.erpnext import (
    get_headers,
    get_sales_invoices,
    get_overdue_invoices,
    get_bin_stock,
    get_low_stock_items,
    get_delayed_purchase_orders
)

# -------------------
# BASIC ENV CHECK
# -------------------

def test_env_variables_exist():
    assert os.getenv("ERP_URL")
    assert os.getenv("ERP_API_KEY")
    assert os.getenv("ERP_API_SECRET")


# -------------------
# HEADERS
# -------------------

def test_get_headers_real():
    headers = get_headers()
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("token ")
    assert headers["Accept"] == "application/json"


# -------------------
# SALES INVOICES
# -------------------

def test_get_sales_invoices_real():
    invoices = get_sales_invoices(limit=5)

    assert isinstance(invoices, list)

    if invoices:
        inv = invoices[0]
        assert "name" in inv
        assert "customer" in inv
        assert "due_date" in inv
        assert inv["outstanding_amount"] >= 0


# -------------------
# OVERDUE INVOICES
# -------------------

def test_get_overdue_invoices_real():
    result = get_overdue_invoices(limit=10)

    assert isinstance(result, dict)
    assert "kpis" in result
    assert "data" in result

    for inv in result["data"]:
        assert inv["days_overdue"] >= 8
        assert inv["risk_level"] in ["Medium", "High"]
        assert inv["outstanding_amount"] > 0


# -------------------
# BIN STOCK
# -------------------

def test_get_bin_stock_real():
    result = get_bin_stock(limit=10)

    assert "count" in result
    assert "data" in result
    assert isinstance(result["data"], list)

    if result["data"]:
        item = result["data"][0]

        assert "item_code" in item
        assert "total_qty" in item

        # ERPNext allows negative stock  →  just validate type
        assert isinstance(item["total_qty"], (int, float))

        assert "warehouses" in item
        assert isinstance(item["warehouses"], list)



# -------------------
# LOW STOCK ITEMS
# -------------------

def test_get_low_stock_items_real():
    result = get_low_stock_items(limit=20)

    assert "data" in result
    assert "high_count" in result
    assert "medium_count" in result

    for item in result["data"]:
        assert item["warehouse"] in ["Finished Goods - SD", "Stores - SD"]
        assert item["risk_level"] in ["High", "Medium"]

        if item["risk_level"] == "High":
            assert item["actual_qty"] < 30
        if item["risk_level"] == "Medium":
            assert 30 <= item["actual_qty"] <= 60


# -------------------
# DELAYED PURCHASE ORDERS
# -------------------

def test_get_delayed_purchase_orders_real():
    result = get_delayed_purchase_orders(limit=10)

    assert "data" in result
    assert "high_count" in result
    assert "medium_count" in result

    for po in result["data"]:
        assert po["stuck_days"] >= 7
        assert po["risk_level"] in ["High", "Medium"]





