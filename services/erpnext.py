import os
import requests
from datetime import date, datetime
from dotenv import load_dotenv

load_dotenv()

ERP_URL = os.getenv("ERP_URL", "").rstrip("/")
API_KEY = os.getenv("ERP_API_KEY")
API_SECRET = os.getenv("ERP_API_SECRET")


def get_headers():
    """Build authorization headers for ERPNext API."""
    if not API_KEY or not API_SECRET:
        raise ValueError("Missing ERP_API_KEY or ERP_API_SECRET in .env")
    return {
        "Authorization": f"token {API_KEY}:{API_SECRET}",
        "Accept": "application/json"
    }


def get_sales_invoices(limit: int = 50):
    """
    Fetch Sales Invoices from ERPNext.
    
    Returns submitted invoices sorted by due_date (oldest first).
    """
    if not ERP_URL:
        raise ValueError("Missing ERP_URL in .env")
    
    fields = [
        "name",
        "customer",
        "posting_date",
        "due_date",
        "status",
        "outstanding_amount",
        "grand_total",
        "currency"
    ]
    
    filters = [
        ["docstatus", "=", 1]  # Only submitted invoices
    ]
    
    params = {
        "fields": str(fields).replace("'", '"'),
        "filters": str(filters).replace("'", '"'),
        "order_by": "due_date asc",
        "limit_page_length": limit
    }
    
    url = f"{ERP_URL}/api/resource/Sales Invoice"
    
    response = requests.get(url, headers=get_headers(), params=params)
    response.raise_for_status()
    
    data = response.json()
    return data.get("data", [])


from datetime import date, datetime
import requests

from datetime import date, datetime
import requests

def get_overdue_invoices(
    limit: int = 50,
    customer: str = None,
    days_medium_min: int = 8,
    days_medium_max: int = 14,
    days_high_min: int = 15
):
    """
    Fetch overdue Sales Invoices from ERPNext with risk scoring.

    Overdue invoices:
    - docstatus = 1 (Submitted)
    - status != Paid
    - due_date < today
    - outstanding_amount > 0

    Risk levels:
    - Medium: 8–14 days overdue
    - High: 15+ days overdue
    """

    if not ERP_URL:
        raise ValueError("Missing ERP_URL in .env")

    today = date.today()
    today_str = today.isoformat()

    fields = [
        "name",
        "customer",
        "posting_date",
        "due_date",
        "status",
        "outstanding_amount",
        "grand_total",
        "currency"
    ]

    filters = [
        ["docstatus", "=", 1],
        ["status", "!=", "Paid"],
        ["due_date", "<", today_str],
        ["outstanding_amount", ">", 0]
    ]

    if customer:
        filters.append(["customer", "=", customer])

    params = {
        "fields": str(fields).replace("'", '"'),
        "filters": str(filters).replace("'", '"'),
        "order_by": "due_date asc",
        "limit_page_length": limit
    }

    url = f"{ERP_URL}/api/resource/Sales Invoice"

    response = requests.get(url, headers=get_headers(), params=params)
    response.raise_for_status()

    raw_data = response.json().get("data", [])

    result = []
    medium_count = 0
    high_count = 0

    for inv in raw_data:
        due_date_str = inv.get("due_date")
        if not due_date_str:
            continue

        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        days_overdue = (today - due_date).days

        # Risk rules:
        if days_overdue >= days_high_min:
            risk_level = "High"
            high_count += 1

        elif days_medium_min <= days_overdue <= days_medium_max:
            risk_level = "Medium"
            medium_count += 1

        else:
            # Ignore invoices overdue < 8 days
            continue

        result.append({
            "invoice_id": inv.get("name"),
            "customer": inv.get("customer"),
            "posting_date": inv.get("posting_date"),
            "due_date": due_date_str,
            "days_overdue": days_overdue,
            "status": inv.get("status"),
            "outstanding_amount": inv.get("outstanding_amount"),
            "grand_total": inv.get("grand_total"),
            "currency": inv.get("currency"),
            "risk_level": risk_level
        })

    # Calculate KPIs
    total_outstanding_overdue = sum(inv["outstanding_amount"] for inv in result)
    
    # Find most overdue invoice
    most_overdue_invoice = None
    if result:
        most_overdue_invoice = max(result, key=lambda x: x["days_overdue"])

    return {
        # KPIs at the top
        "kpis": {
            "overdue_invoices_count": len(result),
            "total_outstanding_overdue_amount": total_outstanding_overdue,
            "most_overdue_days": most_overdue_invoice["days_overdue"] if most_overdue_invoice else 0,
            "most_overdue_invoice_id": most_overdue_invoice["invoice_id"] if most_overdue_invoice else None,
            "most_overdue_customer": most_overdue_invoice["customer"] if most_overdue_invoice else None
        },
        "count": len(result),
        "medium_count": medium_count,
        "high_count": high_count,
        "data": result
    }

def get_bin_stock(
    limit: int = 100,
    item_code: str = None,
    warehouse: str = None,
    aggregate: bool = True
):
    """
    Fetch current stock quantity per item using the Bin DocType.
    
    The Bin DocType stores the current stock quantity per item/warehouse.
    
    Args:
        limit: Maximum number of entries to return (pagination)
        item_code: Filter by specific item code
        warehouse: Filter by specific warehouse
        aggregate: If True, aggregate results by item_code to return total qty across all warehouses
    
    Returns:
        JSON response with count and stock data
    """
    if not ERP_URL:
        raise ValueError("Missing ERP_URL in .env")
    
    fields = [
        "name",
        "item_code",
        "warehouse",
        "actual_qty"
    ]
    
    filters = []
    
    # Filter by item_code
    if item_code:
        filters.append(["item_code", "=", item_code])
    
    # Filter by warehouse
    if warehouse:
        filters.append(["warehouse", "=", warehouse])
    
    params = {
        "fields": str(fields).replace("'", '"'),
        "order_by": "actual_qty asc",
        "limit_page_length": limit
    }
    
    # Only add filters if there are any
    if filters:
        params["filters"] = str(filters).replace("'", '"')
    
    url = f"{ERP_URL}/api/resource/Bin"
    
    response = requests.get(url, headers=get_headers(), params=params)
    response.raise_for_status()
    
    data = response.json().get("data", [])
    
    # Aggregate by item_code if requested
    if aggregate and not item_code:
        aggregated = {}
        for entry in data:
            code = entry.get("item_code")
            qty = entry.get("actual_qty", 0) or 0
            if code in aggregated:
                aggregated[code]["total_qty"] += qty
                aggregated[code]["warehouses"].append({
                    "warehouse": entry.get("warehouse"),
                    "actual_qty": qty
                })
            else:
                aggregated[code] = {
                    "item_code": code,
                    "total_qty": qty,
                    "warehouses": [{
                        "warehouse": entry.get("warehouse"),
                        "actual_qty": qty
                    }]
                }
        
        # Convert to list and sort by total_qty ascending
        result = list(aggregated.values())
        result.sort(key=lambda x: x["total_qty"])
        
        return {
            "count": len(result),
            "data": result
        }
    
    return {
        "count": len(data),
        "data": data
    }


def get_low_stock_items(
    limit: int = 500,
    warehouse: str = None,
    item_code: str = None
):
    """
Fetch low stock items from Bin ONLY for:
- Finished Goods - SD
- Stores - SD

Risk levels:
- High: actual_qty < 30 (including negative quantities)
- Medium: 30 <= actual_qty < 60
- Ignored: actual_qty >= 60

Returns:
  Only Medium/High risk items, sorted by actual_qty ascending,
  filtered to warehouses: Finished Goods - SD and Stores - SD.
    """
    if not ERP_URL:
        raise ValueError("Missing ERP_URL in .env")

    ALLOWED_WAREHOUSES = ["Finished Goods - SD", "Stores - SD"]

    fields = [
        "name",
        "item_code",
        "warehouse",
        "actual_qty"
    ]

    filters = []

    # ✅ If warehouse is provided, allow only if it's in allowed list
    if warehouse:
        if warehouse not in ALLOWED_WAREHOUSES:
            return {
                "count": 0,
                "high_count": 0,
                "medium_count": 0,
                "data": []
            }
        filters.append(["warehouse", "=", warehouse])
    else:
        # ✅ Only show these 2 warehouses
        filters.append(["warehouse", "in", ALLOWED_WAREHOUSES])

    if item_code:
        filters.append(["item_code", "=", item_code])

    params = {
        "fields": str(fields).replace("'", '"'),
        "filters": str(filters).replace("'", '"'),
        "order_by": "actual_qty asc",
        "limit_page_length": limit
    }

    url = f"{ERP_URL}/api/resource/Bin"

    response = requests.get(url, headers=get_headers(), params=params)
    response.raise_for_status()

    raw_data = response.json().get("data", [])

    result = []
    high_count = 0
    medium_count = 0

    for entry in raw_data:
        qty = entry.get("actual_qty", 0) or 0

        # ✅ High for qty < 0 (negative stock only)
        if qty < 0:
            risk_level = "High"
            high_count += 1

        # ✅ Medium for 30 <= qty <= 60
        elif 30 <= qty <= 60:
            risk_level = "Medium"
            medium_count += 1

        else:
            # Ignore qty 0-29 and qty > 60
            continue

        result.append({
            "item_code": entry.get("item_code"),
            "warehouse": entry.get("warehouse"),
            "actual_qty": qty,
            "risk_level": risk_level
        })

    # Sort: lowest qty first (negatives at top)
    result.sort(key=lambda x: x["actual_qty"])

    # Return top 50 results
    top_50 = result[:50]

    return {
        "count": len(top_50),
        "high_count": sum(1 for x in top_50 if x["risk_level"] == "High"),
        "medium_count": sum(1 for x in top_50 if x["risk_level"] == "Medium"),
        "data": top_50
    }


def get_delayed_purchase_orders(limit: int = 100):
    """
    Fetch Purchase Orders that are delayed (stuck) with no/partial receipt.
    
    A PO is considered delayed/stuck if:
    - docstatus = 1 (Submitted)
    - status in ["To Receive", "To Receive and Bill"]
    - today - transaction_date >= 7 days
    - per_received < 100 (not fully received)
    
    Risk levels:
    - Medium: 7 <= stuck_days <= 14
    - High: stuck_days > 14
    
    Returns:
        List of delayed POs sorted by stuck_days descending (most delayed first)
    """
    if not ERP_URL:
        raise ValueError("Missing ERP_URL in .env")
    
    today = date.today()
    
    # Fetch Purchase Orders with status "To Receive" or "To Receive and Bill"
    # per_received < 100 means not fully received yet
    po_fields = [
        "name",
        "supplier",
        "transaction_date",
        "status",
        "grand_total",
        "currency",
        "per_received"
    ]
    
    po_filters = [
        ["docstatus", "=", 1],
        ["status", "in", ["To Receive", "To Receive and Bill"]]
    ]
    
    po_params = {
        "fields": str(po_fields).replace("'", '"'),
        "filters": str(po_filters).replace("'", '"'),
        "order_by": "transaction_date asc",
        "limit_page_length": limit
    }
    
    po_url = f"{ERP_URL}/api/resource/Purchase Order"
    response = requests.get(po_url, headers=get_headers(), params=po_params)
    response.raise_for_status()
    
    purchase_orders = response.json().get("data", [])
    
    # Filter POs that are delayed >= 7 days
    result = []
    high_count = 0
    medium_count = 0
    
    for po in purchase_orders:
        po_name = po.get("name")
        per_received = po.get("per_received", 0) or 0
        
        # Skip if fully received
        if per_received >= 100:
            continue
        
        # Calculate stuck days
        transaction_date_str = po.get("transaction_date")
        if not transaction_date_str:
            continue
        
        try:
            transaction_date = datetime.strptime(transaction_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        
        stuck_days = (today - transaction_date).days
        
        # Skip if not delayed (less than 7 days)
        if stuck_days < 7:
            continue
        
        # Assign risk level
        if stuck_days > 14:
            risk_level = "High"
            high_count += 1
        elif 7 <= stuck_days <= 14:
            risk_level = "Medium"
            medium_count += 1
        else:
            continue
        
        result.append({
            "po": po_name,
            "supplier": po.get("supplier"),
            "transaction_date": transaction_date_str,
            "stuck_days": stuck_days,
            "status": po.get("status"),
            "grand_total": po.get("grand_total"),
            "currency": po.get("currency"),
            "risk_level": risk_level
        })
    
    # Sort by stuck_days descending (most delayed first)
    result.sort(key=lambda x: x["stuck_days"], reverse=True)
    
    return {
        "count": len(result),
        "high_count": high_count,
        "medium_count": medium_count,
        "data": result
    }


# Example usage:
# if __name__ == "__main__":
#     delayed_pos = get_delayed_purchase_orders()
#     print(f"Found {delayed_pos['count']} delayed POs")
#     print(f"High Risk: {delayed_pos['high_count']}, Medium Risk: {delayed_pos['medium_count']}")
#     for po in delayed_pos['data']:
#         print(f"  {po['po']} | {po['supplier']} | {po['stuck_days']} days | {po['risk_level']}")
