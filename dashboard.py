"""
ERPNext Risk Radar - Dashboard Server
Run this file to start the dashboard: python dashboard.py
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from services.erpnext import get_sales_invoices, get_overdue_invoices, get_low_stock_items, get_delayed_purchase_orders
import requests
import os

app = FastAPI(title="ERPNext Risk Radar Dashboard")

# Static directory path
static_dir = os.path.join(os.path.dirname(__file__), "static")


@app.get("/")
def dashboard():
    """Serve the dashboard HTML"""
    return FileResponse(os.path.join(static_dir, "dashboard.html"))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/invoices")
def invoices(limit: int = 50):
    """Fetch Sales Invoices from ERPNext."""
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
    days_medium_max: int = Query(14, description="Max days for Medium risk"),
    days_high_min: int = Query(15, description="Min days for High risk")
):
    """Fetch overdue Sales Invoices with risk scoring."""
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


@app.get("/inventory/low-stock")
def low_stock_items(
    limit: int = Query(100, description="Max entries to fetch from ERPNext"),
    warehouse: str = Query(None, description="Filter by warehouse"),
    item_code: str = Query(None, description="Filter by item code")
):
    """Fetch inventory items with low stock risk scoring using Bin DocType."""
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
    - No Purchase Receipt linked
    - Stuck for >= 7 days
    
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


# Mount static files AFTER defining all routes
app.mount("/static", StaticFiles(directory=static_dir), name="static")


if __name__ == "__main__":
    import uvicorn
    print("🎯 Starting ERPNext Risk Radar Dashboard...")
    print("📊 Open http://localhost:8082 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8082)
