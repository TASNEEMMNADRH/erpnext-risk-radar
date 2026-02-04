# backend/test/test_api.py
import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import requests

from app import app

client = TestClient(app)


class TestAPI(unittest.TestCase):

    def test_health(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_root_redirect(self):
        response = client.get("/", follow_redirects=False)
        self.assertIn(response.status_code, [307, 302])
        self.assertIn("location", response.headers)
        self.assertTrue(response.headers["location"].endswith("/static/dashboard.html"))

    @patch('app.get_sales_invoices')
    def test_get_sales_invoices(self, mock_get_sales_invoices):
        # Mock return value with 2 fake invoices
        mock_get_sales_invoices.return_value = [
            {"invoice_id": "INV-001",
            "customer": "Customer A",
            "outstanding_amount": 1000},

            {"invoice_id": "INV-002",
            "customer": "Customer B",
            "outstanding_amount": 2000}
        ]
        
        # Call the endpoint with limit=2
        response = client.get("/invoices?limit=2")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("count", json_data)
        self.assertIn("data", json_data)
        self.assertEqual(json_data["count"], 2)
        self.assertEqual(len(json_data["data"]), 2)
        
        # Verify limit parameter was passed correctly
        mock_get_sales_invoices.assert_called_once_with(limit=2)

    @patch('app.get_sales_invoices')
    def test_get_sales_invoices_default_limit(self, mock_get_sales_invoices):
        # Mock return value with empty list
        mock_get_sales_invoices.return_value = []
        
        # Call the endpoint without limit parameter (should use default=50)
        response = client.get("/invoices")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data["count"], 0)
        
        # Verify default limit parameter (50) was passed
        mock_get_sales_invoices.assert_called_once_with(limit=50)

    @patch('app.get_sales_invoices')
    def test_invoices_value_error_returns_500(self, mock_get_sales_invoices):
        # Mock to raise ValueError
        mock_get_sales_invoices.side_effect = ValueError("Invalid data")
        
        # Call the endpoint
        response = client.get("/invoices?limit=10")
        
        # Assert status code is 500 (ValueError mapped to 500)
        self.assertEqual(response.status_code, 500)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertEqual(json_data["detail"], "Invalid data")
        
        # Verify the service function was invoked
        mock_get_sales_invoices.assert_called_once_with(limit=10)

    @patch('app.get_sales_invoices')
    def test_invoices_error_401(self, mock_get_sales_invoices):
        # Create a mock response with status_code 401
        mock_response = Mock()
        mock_response.status_code = 401
        
        # Mock to raise HTTPError with 401 status
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_get_sales_invoices.side_effect = http_error
        
        # Call the endpoint
        response = client.get("/invoices?limit=15")
        
        # Assert status code is 401 (HTTPError 401 mapped to 401)
        self.assertEqual(response.status_code, 401)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertEqual(json_data["detail"], "ERPNext authentication failed")
        
        # Verify the service function was invoked
        mock_get_sales_invoices.assert_called_once_with(limit=15)

    @patch('app.get_sales_invoices')
    def test_invoices_erp_error_returns_502(self, mock_get_sales_invoices):
        # Create a mock response with status_code 500
        mock_response = Mock()
        mock_response.status_code = 500
        
        # Mock to raise HTTPError with 500 status
        http_error = requests.exceptions.HTTPError("Server Error")
        http_error.response = mock_response
        mock_get_sales_invoices.side_effect = http_error
        
        # Call the endpoint
        response = client.get("/invoices?limit=25")
        
        # Assert status code is 502 (HTTPError non-401 mapped to 502)
        self.assertEqual(response.status_code, 502)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertIn("ERPNext API error", json_data["detail"])
        
        # Verify the service function was invoked
        mock_get_sales_invoices.assert_called_once_with(limit=25)

    @patch('app.get_sales_invoices')
    def test_invoices_connection_error_returns_502(self, mock_get_sales_invoices):
        # Mock to raise ConnectionError
        mock_get_sales_invoices.side_effect = requests.exceptions.ConnectionError()
        
        # Call the endpoint
        response = client.get("/invoices?limit=20")
        
        # Assert status code is 502 (ConnectionError mapped to 502)
        self.assertEqual(response.status_code, 502)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertEqual(json_data["detail"], "Cannot connect to ERPNext")
        
        # Verify the service function was invoked
        mock_get_sales_invoices.assert_called_once_with(limit=20)

 






    @patch('app.get_overdue_invoices')
    def test_overdue_invoices(self, mock_get_overdue_invoices):
        # Mock return value with count, medium_count, high_count, and data
        mock_get_overdue_invoices.return_value = {
            "count": 1,
            "medium_count": 0,
            "high_count": 1,
            "data": [
                {
                    "invoice_id": "INV-003",
                    "customer": "Customer C",
                    "outstanding_amount": 5000,
                    "days_overdue": 15,
                    "risk_level": "High"
                }
            ]
        }
        
        # Call the endpoint
        response = client.get("/invoices/overdue?limit=1")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("count", json_data)
        self.assertIn("medium_count", json_data)
        self.assertIn("high_count", json_data)
        self.assertIn("data", json_data)
        self.assertEqual(json_data["count"], 1)
        self.assertEqual(len(json_data["data"]), 1)
        
        # Verify service function was called (days_medium_min has default, not passed by API)
        mock_get_overdue_invoices.assert_called_once()

    @patch('app.get_overdue_invoices')
    def test_overdue_invoices_value_error_returns_500(self, mock_get_overdue_invoices):
        # Mock to raise ValueError
        mock_get_overdue_invoices.side_effect = ValueError("Invalid data")
        
        # Call the endpoint
        response = client.get("/invoices/overdue?limit=10")
        
        # Assert status code is 500
        self.assertEqual(response.status_code, 500)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertEqual(json_data["detail"], "Invalid data")
        
        # Verify the service function was invoked
        mock_get_overdue_invoices.assert_called_once()

    @patch('app.get_overdue_invoices')
    def test_overdue_invoices_http_error_401_returns_401(self, mock_get_overdue_invoices):
        # Create a mock response with status_code 401
        mock_response = Mock()
        mock_response.status_code = 401
        
        # Mock to raise HTTPError with 401 status
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_get_overdue_invoices.side_effect = http_error
        
        # Call the endpoint
        response = client.get("/invoices/overdue?limit=15")
        
        # Assert status code is 401
        self.assertEqual(response.status_code, 401)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertEqual(json_data["detail"], "ERPNext authentication failed")
        
        # Verify the service function was invoked
        mock_get_overdue_invoices.assert_called_once()

    @patch('app.get_overdue_invoices')
    def test_overdue_invoices_http_error_non_401_returns_502(self, mock_get_overdue_invoices):
        # Create a mock response with status_code 500
        mock_response = Mock()
        mock_response.status_code = 500
        
        # Mock to raise HTTPError with 500 status
        http_error = requests.exceptions.HTTPError("Server Error")
        http_error.response = mock_response
        mock_get_overdue_invoices.side_effect = http_error
        
        # Call the endpoint
        response = client.get("/invoices/overdue?limit=20")
        
        # Assert status code is 502
        self.assertEqual(response.status_code, 502)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertIn("ERPNext API error", json_data["detail"])
        
        # Verify the service function was invoked
        mock_get_overdue_invoices.assert_called_once()

    @patch('app.get_overdue_invoices')
    def test_overdue_invoices_connection_error_returns_502(self, mock_get_overdue_invoices):
        # Mock to raise ConnectionError
        mock_get_overdue_invoices.side_effect = requests.exceptions.ConnectionError()
        
        # Call the endpoint
        response = client.get("/invoices/overdue?limit=25")
        
        # Assert status code is 502
        self.assertEqual(response.status_code, 502)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertEqual(json_data["detail"], "Cannot connect to ERPNext")
        
        # Verify the service function was invoked
        mock_get_overdue_invoices.assert_called_once()

    @patch('app.get_bin_stock')
    def test_stock_ledger(self, mock_get_bin_stock):
        # Mock return value
        mock_get_bin_stock.return_value = {
            "count": 2,
            "data": [
                {
                    "item_code": "ITEM-001",
                    "total_qty": 120,
                    "warehouses": [
                        {"warehouse": "Stores", "actual_qty": 70},
                        {"warehouse": "Finished Goods", "actual_qty": 50}
                    ]
                },
                {
                    "item_code": "ITEM-002",
                    "total_qty": 20,
                    "warehouses": [
                        {"warehouse": "Stores", "actual_qty": 20}
                    ]
                }
            ]
        }
        
        # Call the endpoint
        response = client.get("/stock-ledger?limit=2&aggregate=true")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("count", json_data)
        self.assertIn("data", json_data)
        self.assertEqual(json_data["count"], 2)
        self.assertEqual(len(json_data["data"]), 2)
        
        # Verify parameters passed correctly
        mock_get_bin_stock.assert_called_once_with(
            limit=2,
            item_code=None,
            warehouse=None,
            aggregate=True
        )

    @patch('app.get_bin_stock')
    def test_stock_ledger_value_error_returns_500(self, mock_get_bin_stock):
        # Mock to raise ValueError
        mock_get_bin_stock.side_effect = ValueError("Invalid data")
        
        # Call the endpoint
        response = client.get("/stock-ledger?limit=10")
        
        # Assert status code is 500
        self.assertEqual(response.status_code, 500)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertEqual(json_data["detail"], "Invalid data")
        
        # Verify the service function was invoked
        mock_get_bin_stock.assert_called_once_with(
            limit=10,
            item_code=None,
            warehouse=None,
            aggregate=True
        )

    @patch('app.get_bin_stock')
    def test_stock_ledger_http_error_401_returns_401(self, mock_get_bin_stock):
        # Create a mock response with status_code 401
        mock_response = Mock()
        mock_response.status_code = 401
        
        # Mock to raise HTTPError with 401 status
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_get_bin_stock.side_effect = http_error
        
        # Call the endpoint
        response = client.get("/stock-ledger?limit=15")
        
        # Assert status code is 401
        self.assertEqual(response.status_code, 401)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertEqual(json_data["detail"], "ERPNext authentication failed")
        
        # Verify the service function was invoked
        mock_get_bin_stock.assert_called_once_with(
            limit=15,
            item_code=None,
            warehouse=None,
            aggregate=True
        )

    @patch('app.get_bin_stock')
    def test_stock_ledger_http_error_non_401_returns_502(self, mock_get_bin_stock):
        # Create a mock response with status_code 500
        mock_response = Mock()
        mock_response.status_code = 500
        
        # Mock to raise HTTPError with 500 status
        http_error = requests.exceptions.HTTPError("Server Error")
        http_error.response = mock_response
        mock_get_bin_stock.side_effect = http_error
        
        # Call the endpoint
        response = client.get("/stock-ledger?limit=20")
        
        # Assert status code is 502
        self.assertEqual(response.status_code, 502)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertIn("ERPNext API error", json_data["detail"])
        
        # Verify the service function was invoked
        mock_get_bin_stock.assert_called_once_with(
            limit=20,
            item_code=None,
            warehouse=None,
            aggregate=True
        )

    @patch('app.get_bin_stock')
    def test_stock_ledger_connection_error_returns_502(self, mock_get_bin_stock):
        # Mock to raise ConnectionError
        mock_get_bin_stock.side_effect = requests.exceptions.ConnectionError()
        
        # Call the endpoint
        response = client.get("/stock-ledger?limit=25")
        
        # Assert status code is 502
        self.assertEqual(response.status_code, 502)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertEqual(json_data["detail"], "Cannot connect to ERPNext")
        
        # Verify the service function was invoked
        mock_get_bin_stock.assert_called_once_with(
            limit=25,
            item_code=None,
            warehouse=None,
            aggregate=True
        )

    @patch('app.get_low_stock_items')
    def test_inventory_low_stock(self, mock_get_low_stock_items):
        # Mock return value with 2 low stock items
        mock_get_low_stock_items.return_value = {
            "count": 2,
            "data": [
                {
                    "item_code": "ITEM-LOW-001",
                    "warehouse": "Finished Goods - SD",
                    "actual_qty": 5,
                    "risk_level": "High"
                },
                {
                    "item_code": "ITEM-LOW-002",
                    "warehouse": "Stores",
                    "actual_qty": 46,
                    "risk_level": "Medium"
                }
            ]
        }
        
        # Call the endpoint
        response = client.get("/inventory/low-stock?limit=2")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("count", json_data)
        self.assertIn("data", json_data)
        self.assertEqual(json_data["count"], 2)
        self.assertEqual(len(json_data["data"]), 2)
        
        # Assert the mock was called with correct parameters
        mock_get_low_stock_items.assert_called_once_with(limit=2, warehouse=None, item_code=None)

    @patch('app.get_low_stock_items')
    def test_inventory_low_stock_with_warehouse_filter(self, mock_get_low_stock_items):
        # Mock return value for warehouse-specific query
        mock_get_low_stock_items.return_value = {
            "count": 1,
            "data": [
                {
                    "item_code": "ITEM-LOW-003",
                    "warehouse": "Stores",
                    "actual_qty": 10,
                    "risk_level": "High"
                }
            ]
        }
        
        # Call the endpoint with warehouse filter
        response = client.get("/inventory/low-stock?warehouse=Stores&limit=10")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data["count"], 1)
        
        # Assert the mock was called with warehouse parameter
        mock_get_low_stock_items.assert_called_once_with(limit=10, warehouse="Stores", item_code=None)

    @patch('app.get_low_stock_items')
    def test_inventory_low_stock_with_item_code_filter(self, mock_get_low_stock_items):
        # Mock return value for item_code-specific query
        mock_get_low_stock_items.return_value = {
            "count": 1,
            "data": [
                {
                    "item_code": "ITEM-123",
                    "warehouse": "Stores",
                    "actual_qty": 20,
                    "risk_level": "Medium"
                }
            ]
        }
        
        # Call the endpoint with item_code filter
        response = client.get("/inventory/low-stock?item_code=ITEM-123&limit=15")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data["count"], 1)
        
        # Assert the mock was called with item_code parameter
        mock_get_low_stock_items.assert_called_once_with(limit=15, warehouse=None, item_code="ITEM-123")

    @patch('app.get_low_stock_items')
    def test_inventory_low_stock_value_error_returns_500(self, mock_get_low_stock_items):
        # Mock to raise ValueError
        mock_get_low_stock_items.side_effect = ValueError("Invalid data")
        
        # Call the endpoint
        response = client.get("/inventory/low-stock?limit=10")
        
        # Assert status code is 500
        self.assertEqual(response.status_code, 500)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertEqual(json_data["detail"], "Invalid data")
        
        # Verify the service function was invoked
        mock_get_low_stock_items.assert_called_once_with(limit=10, warehouse=None, item_code=None)

    @patch('app.get_low_stock_items')
    def test_inventory_low_stock_http_error_401_returns_401(self, mock_get_low_stock_items):
        # Create a mock response with status_code 401
        mock_response = Mock()
        mock_response.status_code = 401
        
        # Mock to raise HTTPError with 401 status
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_get_low_stock_items.side_effect = http_error
        
        # Call the endpoint
        response = client.get("/inventory/low-stock?limit=15")
        
        # Assert status code is 401
        self.assertEqual(response.status_code, 401)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertEqual(json_data["detail"], "ERPNext authentication failed")
        
        # Verify the service function was invoked
        mock_get_low_stock_items.assert_called_once_with(limit=15, warehouse=None, item_code=None)

    @patch('app.get_low_stock_items')
    def test_inventory_low_stock_http_error_non_401_returns_502(self, mock_get_low_stock_items):
        # Create a mock response with status_code 500
        mock_response = Mock()
        mock_response.status_code = 500
        
        # Mock to raise HTTPError with 500 status
        http_error = requests.exceptions.HTTPError("Server Error")
        http_error.response = mock_response
        mock_get_low_stock_items.side_effect = http_error
        
        # Call the endpoint
        response = client.get("/inventory/low-stock?limit=20")
        
        # Assert status code is 502
        self.assertEqual(response.status_code, 502)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertIn("ERPNext API error", json_data["detail"])
        
        # Verify the service function was invoked
        mock_get_low_stock_items.assert_called_once_with(limit=20, warehouse=None, item_code=None)

    @patch('app.get_low_stock_items')
    def test_inventory_low_stock_connection_error_returns_502(self, mock_get_low_stock_items):
        # Mock to raise ConnectionError
        mock_get_low_stock_items.side_effect = requests.exceptions.ConnectionError()
        
        # Call the endpoint
        response = client.get("/inventory/low-stock?limit=25")
        
        # Assert status code is 502
        self.assertEqual(response.status_code, 502)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertEqual(json_data["detail"], "Cannot connect to ERPNext")
        
        # Verify the service function was invoked
        mock_get_low_stock_items.assert_called_once_with(limit=25, warehouse=None, item_code=None)




    @patch('app.get_delayed_purchase_orders')
    def test_purchase_orders_delayed(self, mock_get_delayed_purchase_orders):
        # Mock return value with 2 delayed purchase orders
        mock_get_delayed_purchase_orders.return_value = {
            "count": 2,
            "data": [
                {
                    "po_number": "PO-2026-001",
                    "supplier": "Supplier A",
                    "days_delayed": 10,
                    "risk_level": "Medium"
                },
                {
                    "po_number": "PO-2026-002",
                    "supplier": "Supplier B",
                    "days_delayed": 20,
                    "risk_level": "High"
                }
            ]
        }
        
        # Call the endpoint
        response = client.get("/purchase-orders/delayed?limit=2")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("count", json_data)
        self.assertIn("data", json_data)
        self.assertEqual(json_data["count"], 2)
        self.assertEqual(len(json_data["data"]), 2)
        
        # Assert the mock was called with correct parameters
        mock_get_delayed_purchase_orders.assert_called_once_with(limit=2)

    @patch('app.get_delayed_purchase_orders')
    def test_purchase_orders_delayed_default_limit(self, mock_get_delayed_purchase_orders):
        # Mock return value with empty list
        mock_get_delayed_purchase_orders.return_value = {
            "count": 0,
            "data": []
        }
        
        # Call the endpoint without limit parameter (should use default=100)
        response = client.get("/purchase-orders/delayed")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data["count"], 0)
        
        # Verify default limit parameter (100) was passed
        mock_get_delayed_purchase_orders.assert_called_once_with(limit=100)

    @patch('app.get_delayed_purchase_orders')
    def test_purchase_orders_delayed_value_error_returns_500(self, mock_get_delayed_purchase_orders):
        # Mock to raise ValueError
        mock_get_delayed_purchase_orders.side_effect = ValueError("Invalid data")
        
        # Call the endpoint
        response = client.get("/purchase-orders/delayed?limit=10")
        
        # Assert status code is 500
        self.assertEqual(response.status_code, 500)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertEqual(json_data["detail"], "Invalid data")
        
        # Verify the service function was invoked
        mock_get_delayed_purchase_orders.assert_called_once_with(limit=10)

    @patch('app.get_delayed_purchase_orders')
    def test_purchase_orders_delayed_http_error_401_returns_401(self, mock_get_delayed_purchase_orders):
        # Create a mock response with status_code 401
        mock_response = Mock()
        mock_response.status_code = 401
        
        # Mock to raise HTTPError with 401 status
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_get_delayed_purchase_orders.side_effect = http_error
        
        # Call the endpoint
        response = client.get("/purchase-orders/delayed?limit=15")
        
        # Assert status code is 401
        self.assertEqual(response.status_code, 401)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertEqual(json_data["detail"], "ERPNext authentication failed")
        
        # Verify the service function was invoked
        mock_get_delayed_purchase_orders.assert_called_once_with(limit=15)

    @patch('app.get_delayed_purchase_orders')
    def test_purchase_orders_delayed_http_error_non_401_returns_502(self, mock_get_delayed_purchase_orders):
        # Create a mock response with status_code 500
        mock_response = Mock()
        mock_response.status_code = 500
        
        # Mock to raise HTTPError with 500 status
        http_error = requests.exceptions.HTTPError("Server Error")
        http_error.response = mock_response
        mock_get_delayed_purchase_orders.side_effect = http_error
        
        # Call the endpoint
        response = client.get("/purchase-orders/delayed?limit=20")
        
        # Assert status code is 502
        self.assertEqual(response.status_code, 502)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertIn("ERPNext API error", json_data["detail"])
        
        # Verify the service function was invoked
        mock_get_delayed_purchase_orders.assert_called_once_with(limit=20)

    @patch('app.get_delayed_purchase_orders')
    def test_purchase_orders_delayed_connection_error_returns_502(self, mock_get_delayed_purchase_orders):
        # Mock to raise ConnectionError
        mock_get_delayed_purchase_orders.side_effect = requests.exceptions.ConnectionError()
        
        # Call the endpoint
        response = client.get("/purchase-orders/delayed?limit=25")
        
        # Assert status code is 502
        self.assertEqual(response.status_code, 502)
        json_data = response.json()
        self.assertIn("detail", json_data)
        self.assertEqual(json_data["detail"], "Cannot connect to ERPNext")
        
        # Verify the service function was invoked
        mock_get_delayed_purchase_orders.assert_called_once_with(limit=25)


if __name__ == "__main__":
    unittest.main()






