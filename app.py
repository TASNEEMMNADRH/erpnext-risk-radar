from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from services.erpnext import get_sales_invoices, get_overdue_invoices, get_bin_stock, get_low_stock_items, get_delayed_purchase_orders
import requests

app = FastAPI(title="ERPNext Risk Radar API")

# Mount static files for dashboard
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    """Redirect to dashboard"""
    return RedirectResponse(url="/static/dashboard.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/invoices")
def invoices(limit: int = 50):
    """
    Fetch Sales Invoices from ERPNext.
    
    - Returns submitted invoices sorted by due_date (oldest first)
    - Use ?limit=N to control number of results
    """
    try:
        data = get_sales_invoices(limit=limit)
        return {"count": len(data), "data": data}
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="ERPNext authentication failed")
        raise HTTPException(status_code=502, detail=f"ERPNext API error: {e}")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=502, detail="Cannot connect to ERPNext")


@app.get("/invoices/overdue")
def overdue_invoices(
    limit: int = Query(50, description="Max number of invoices to return"),
    customer: str = Query(None, description="Filter by customer name"),
    days_medium_max: int = Query(7, description="Max days for Medium risk (default 7)"),
    days_high_min: int = Query(8, description="Min days for High risk (default 8)")
):
    """
    Fetch overdue Sales Invoices with risk scoring.
    
    Overdue = due_date < today AND status != Paid AND outstanding > 0
    
    Risk levels:
    - Medium: 1 to days_medium_max days overdue
    - High: >= days_high_min days overdue
    """
    try:
        return get_overdue_invoices(
            limit=limit,
            customer=customer,
            days_medium_max=days_medium_max,
            days_high_min=days_high_min
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="ERPNext authentication failed")
        raise HTTPException(status_code=502, detail=f"ERPNext API error: {e}")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=502, detail="Cannot connect to ERPNext")


@app.get("/stock-ledger")
def stock_ledger(
    limit: int = Query(100, description="Max number of entries to return"),
    item_code: str = Query(None, description="Filter by item code"),
    warehouse: str = Query(None, description="Filter by warehouse"),
    aggregate: bool = Query(True, description="Aggregate by item_code to get total qty across warehouses")
):
    """
    Fetch current stock quantity per item using the Bin DocType.
    
    - Returns current stock levels from ERPNext Bin
    - Use ?limit=N to control number of results
    - Use ?item_code=ITEM-001 to filter by item
    - Use ?warehouse=Stores to filter by warehouse
    - Use ?aggregate=true to get total qty per item across all warehouses
    
    Fields returned: item_code, warehouse, actual_qty (current quantity)
    When aggregated: item_code, total_qty, warehouses (list with breakdown)
    """
    try:
        return get_bin_stock(
            limit=limit,
            item_code=item_code,
            warehouse=warehouse,
            aggregate=aggregate
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="ERPNext authentication failed")
        raise HTTPException(status_code=502, detail=f"ERPNext API error: {e}")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=502, detail="Cannot connect to ERPNext")


@app.get("/inventory/low-stock")
def low_stock_items(
    limit: int = Query(100, description="Max entries to fetch from ERPNext"),
    warehouse: str = Query(None, description="Filter by warehouse"),
    item_code: str = Query(None, description="Filter by item code")
):
    """
    Fetch inventory items with low stock risk scoring using Bin DocType.
    
    Risk levels based on actual_qty:
    - High: actual_qty < 30 (critical stock level)
    - Medium: 30 <= actual_qty < 60 (low stock warning)
    - Ignored: actual_qty >= 60 (sufficient stock)
    
    Returns items sorted by lowest quantity first.
    
    Fields returned: item_code, warehouse, actual_qty, risk_level
    """
    try:
        return get_low_stock_items(
            limit=limit,
            warehouse=warehouse,
            item_code=item_code
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="ERPNext authentication failed")
        raise HTTPException(status_code=502, detail=f"ERPNext API error: {e}")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=502, detail="Cannot connect to ERPNext")


@app.get("/purchase-orders/delayed")
def delayed_purchase_orders(
    limit: int = Query(100, description="Max POs to fetch from ERPNext")
):
    """
    Fetch delayed Purchase Orders with no Purchase Receipt.
    
    A PO is delayed if:
    - Status: To Receive or To Receive and Bill
    - Stuck for >= 7 days without being received
    
    Risk levels:
    - Medium: 7-14 days stuck
    - High: > 14 days stuck
    """
    try:
        return get_delayed_purchase_orders(limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="ERPNext authentication failed")
        raise HTTPException(status_code=502, detail=f"ERPNext API error: {e}")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=502, detail="Cannot connect to ERPNext")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)