import unittest
import re
import os
from playwright.sync_api import sync_playwright, expect

# =========================
# Page Object
# =========================

class DashboardPage:
    URL = os.getenv("BASE_URL", "http://localhost:8082")

    def __init__(self, page):
        self.page = page

    # =========================
    # GENERAL
    # =========================
    @property
    def refresh_button(self):
        return self.page.locator(".refresh-btn")

    def open(self):
        self.page.goto(
             f"{self.URL}/static/dashboard.html", wait_until="networkidle",
 timeout=60000
    )

    def wait_for_invoice_table(self):
        try:
            # חכי שה-page ייטען
            self.page.wait_for_selector("body", timeout=60000)

            # חכי שהתוכן הראשי יופיע
            self.page.wait_for_selector("#table-content", timeout=60000)

        except Exception as e:
            # 📸 Screenshot
            self.page.screenshot(
                path="ui_failure.png",
                full_page=True
            )

            # 🧾 שמירת HTML (מאוד חשוב!)
            with open("ui_failure.html", "w", encoding="utf-8") as f:
                f.write(self.page.content())

            # להכשיל את הטסט עם הודעה ברורה
            raise AssertionError(
                "UI did not load correctly in CI. Screenshot and HTML were saved."
            ) from e


        # 2️⃣ לוודא שהתוכן נטען (טבלה או הודעה)
        self.page.wait_for_selector(
            "#table-content",
            timeout=30000
        )

    def refresh(self):
        self.refresh_button.click()
        self.wait_for_invoice_table()

    # =========================
    # INVOICE – LOCATORS
    # =========================
    @property
    def invoice_filter_button(self):
        return self.page.locator("#invoice-filter-btn")

    @property
    def invoice_risk_high(self):
        return self.page.locator("#invoice-risk-high")

    @property
    def invoice_risk_medium(self):
        return self.page.locator("#invoice-risk-medium")

    @property
    def invoice_days_min(self):
        return self.page.locator("#invoice-days-min")

    @property
    def invoice_days_max(self):
        return self.page.locator("#invoice-days-max")

    @property
    def invoice_amount_min(self):
        return self.page.locator("#invoice-amount-min")

    @property
    def invoice_amount_max(self):
        return self.page.locator("#invoice-amount-max")

    @property
    def invoice_customer(self):
        return self.page.locator("#invoice-customer")

    @property
    def invoice_apply_button(self):
        return self.page.locator("#invoice-filter-dropdown .apply-filter-btn")

    @property
    def invoice_rows(self):
        return self.page.locator("#table-content tbody tr")

    # =========================
    # INVOICE – ACTIONS
    # =========================
    def open_invoice_filter(self):
        self.invoice_filter_button.click()
        self.page.wait_for_selector(
            "#invoice-filter-dropdown.show",
            timeout=5000
        )

    def apply_invoice_filters(self):
        self.invoice_apply_button.click()
        self.page.wait_for_timeout(500)

    # =========================
    # INVOICE – ASSERTIONS
    # =========================
    def assert_invoice_filter_active(self):
        expect(self.invoice_filter_button).to_have_class(
            re.compile("active")
        )

    def assert_invoice_filter_not_active(self):
        expect(self.invoice_filter_button).not_to_have_class(
            re.compile("active")
        )

    def assert_all_invoice_risk(self, risk):
        for i in range(self.invoice_rows.count()):
            badge = self.invoice_rows.nth(i).locator(".risk-badge")
            expect(badge).to_contain_text(risk, ignore_case=True)

    # =========================
    # STOCK – LOCATORS
    # =========================
    @property
    def stock_filter_button(self):
        return self.page.locator("#stock-filter-btn")

    @property
    def stock_risk_high(self):
        return self.page.locator("#stock-risk-high")

    @property
    def stock_risk_medium(self):
        return self.page.locator("#stock-risk-medium")

    @property
    def stock_warehouse(self):
        return self.page.locator("#stock-warehouse")

    @property
    def stock_qty_min(self):
        return self.page.locator("#stock-qty-min")

    @property
    def stock_qty_max(self):
        return self.page.locator("#stock-qty-max")

    @property
    def stock_apply_button(self):
        return self.page.locator("#stock-filter-dropdown .apply-filter-btn")

    @property
    def stock_rows(self):
        return self.page.locator("#stock-table-content tbody tr")

    # =========================
    # STOCK – ACTIONS
    # =========================
    def open_stock_filter(self):
        self.stock_filter_button.click()
        self.page.wait_for_selector(
            "#stock-filter-dropdown",
            state="visible",
            timeout=5000
        )

    def apply_stock_filters(self):
        self.stock_apply_button.click()
        self.page.wait_for_selector(
            "#stock-table-content table",
            timeout=15000
        )

    # =========================
    # STOCK – ASSERTIONS
    # =========================
    def assert_all_stock_from_warehouse(self, warehouse):
        for i in range(self.stock_rows.count()):
            cell = self.stock_rows.nth(i).locator("td").nth(1)
            assert cell.inner_text().strip() == warehouse

    def assert_all_stock_qty_between(self, min_qty, max_qty):
        for i in range(self.stock_rows.count()):
            qty = int(
                self.stock_rows
                .nth(i)
                .locator("td")
                .nth(2)
                .inner_text()
                .strip()
            )
            assert min_qty <= qty <= max_qty

    def assert_all_stock_risk(self, risk):
        for i in range(self.stock_rows.count()):
            badge = self.stock_rows.nth(i).locator(".risk-badge")
            expect(badge).to_contain_text(risk, ignore_case=True)



# =========================
# TESTS
# =========================
class TestDashboardFilters(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
        cls.context = cls.browser.new_context()
        cls.page = cls.context.new_page()

        cls.dashboard = DashboardPage(cls.page)
        cls.dashboard.open()
        cls.dashboard.wait_for_invoice_table()

    @classmethod
    def tearDownClass(cls):
        cls.context.close()
        cls.browser.close()
        cls.playwright.stop()

    def tearDown(self):
        self.dashboard.refresh()

    # =========================
    # INVOICE TESTS
    # =========================
    def test_01_invoice_high_risk_only(self):
        self.dashboard.open_invoice_filter()
        self.dashboard.invoice_risk_medium.uncheck()
        self.dashboard.apply_invoice_filters()

        self.dashboard.assert_invoice_filter_active()
        self.dashboard.assert_all_invoice_risk("High")

    def test_02_invoice_customer_only(self):
        self.dashboard.open_invoice_filter()
        self.dashboard.invoice_customer.select_option(index=1)
        self.dashboard.apply_invoice_filters()

        self.dashboard.assert_invoice_filter_active()
        self.assertGreater(self.dashboard.invoice_rows.count(), 0)

    def test_03_invoice_amount_only(self):
        self.dashboard.open_invoice_filter()
        self.dashboard.invoice_amount_min.fill("1000")
        self.dashboard.invoice_amount_max.fill("5000")
        self.dashboard.apply_invoice_filters()

        self.dashboard.assert_invoice_filter_active()

    def test_04_invoice_days_only(self):
        self.dashboard.open_invoice_filter()
        self.dashboard.invoice_days_min.fill("7")
        self.dashboard.invoice_days_max.fill("30")
        self.dashboard.apply_invoice_filters()

        self.dashboard.assert_invoice_filter_active()

    def test_05_invoice_all_filters(self):
        total_before = self.dashboard.invoice_rows.count()

        self.dashboard.open_invoice_filter()
        self.dashboard.invoice_risk_medium.uncheck()
        self.dashboard.invoice_days_min.fill("7")
        self.dashboard.invoice_days_max.fill("30")
        self.dashboard.invoice_amount_min.fill("500")
        self.dashboard.invoice_amount_max.fill("10000")
        self.dashboard.invoice_customer.select_option(index=1)
        self.dashboard.apply_invoice_filters()

        self.dashboard.assert_invoice_filter_active()
        self.assertLessEqual(
            self.dashboard.invoice_rows.count(),
            total_before
        )

    # =========================
    # STOCK TESTS
    # =========================
    def test_06_stock_filter_by_warehouse(self):
        self.dashboard.open_stock_filter()

        self.page.wait_for_function(
            "() => document.getElementById('stock-warehouse').options.length > 1",
            timeout=10000
        )

        warehouse = (
            self.dashboard.stock_warehouse
            .locator("option")
            .nth(1)
            .get_attribute("value")
        )

        self.dashboard.stock_warehouse.select_option(value=warehouse)
        self.dashboard.apply_stock_filters()
        self.dashboard.assert_all_stock_from_warehouse(warehouse)

    def test_07_stock_filter_by_quantity(self):
        self.dashboard.open_stock_filter()
        self.dashboard.stock_qty_min.fill("20")
        self.dashboard.stock_qty_max.fill("60")
        self.dashboard.apply_stock_filters()

        self.dashboard.assert_all_stock_qty_between(20, 60)

    def test_08_stock_filter_by_warehouse_and_quantity(self):
        self.dashboard.open_stock_filter()

        self.page.wait_for_function(
            "() => document.getElementById('stock-warehouse').options.length > 1",
            timeout=10000
        )

        warehouse = (
            self.dashboard.stock_warehouse
            .locator("option")
            .nth(1)
            .get_attribute("value")
        )

        self.dashboard.stock_warehouse.select_option(value=warehouse)
        self.dashboard.stock_qty_min.fill("20")
        self.dashboard.stock_qty_max.fill("60")
        self.dashboard.apply_stock_filters()

        self.dashboard.assert_all_stock_from_warehouse(warehouse)
        self.dashboard.assert_all_stock_qty_between(20, 60)

    def test_09_stock_filter_by_medium_risk_only(self):
        self.dashboard.open_stock_filter()
        self.dashboard.stock_risk_high.uncheck()
        self.dashboard.stock_risk_medium.check()
        self.dashboard.apply_stock_filters()

        self.dashboard.assert_all_stock_risk("Medium")

    # =========================
    # REFRESH
    # =========================
    def test_10_refresh_resets_invoice_filters(self):
        total_before = self.dashboard.invoice_rows.count()
        self.assertGreater(total_before, 0)

        self.dashboard.open_invoice_filter()
        self.dashboard.invoice_risk_medium.uncheck()
        self.dashboard.invoice_amount_min.fill("1000")
        self.dashboard.apply_invoice_filters()

        self.dashboard.assert_invoice_filter_active()
        self.dashboard.refresh()

        total_after = self.dashboard.invoice_rows.count()
        self.assertEqual(total_after, total_before)
        self.dashboard.assert_invoice_filter_not_active()


if __name__ == "__main__":
    unittest.main()
