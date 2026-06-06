import time
from utilities import common_lib
from playwright.sync_api import Page, expect

class ProductPage:
    '''
    Common login and product page automation
    '''
    def __init__(self, page: Page):
        self.page = page

    def go_to(self, url, log):
        '''
        Navigate to a given URL
        '''
        self.page.goto(url)
        common_lib.debug_print(log, "INFO", f"Redirecting to url: {url}")

    def page_scroll(self, full_height, full_width):
        '''
        Scroll page
        '''
        full_height = self.page.evaluate("() => document.body.scrollHeight")
        full_width = self.page.evaluate("() => document.body.scrollWidth")
        print(f"Full page size: {full_height}px x {full_width}px")
        self.page.evaluate(f"window.scrollTo({full_height},{full_width})")

    def product_details(self, snap_dir, log):
        '''
        Capture product details page
        '''
        self.page.get_by_role("link", name=" Products").click()
        common_lib.debug_print(log, "INFO", "Products Button clicked")
        expect(self.page.get_by_text("All Products")).to_be_visible()
        common_lib.debug_print(log, "INFO", "All Products text visible")
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/AllProductDetails_{ts}.png")

    def get_first_product_details(self, snap_dir):
        '''
        Get details of the first product
        '''
        products = self.page.locator(".features_items .col-sm-4")
        expect(products.nth(0)).to_be_visible()
        products.nth(0).locator("a:has-text('View Product')").click()
        product_details = self.page.locator(".product-information")
        expect(product_details.locator("h2")).to_be_visible()
        expect(product_details.locator("p:has-text('Category')")).to_be_visible()
        expect(product_details.locator("p:has-text('Availability')")).to_be_visible()
        expect(product_details.locator("p:has-text('Condition')")).to_be_visible()
        expect(product_details.locator("p:has-text('Brand')")).to_be_visible()
        print(f"\nProduct Name : {product_details.locator('h2').text_content()}")
        print(f"\nProduct {product_details.locator('p:has-text(\"Category\")').text_content()}")
        print(f"\nProduct Price : {product_details.locator('span').nth(1).text_content()}")
        print(f"\nProduct {product_details.locator('p:has-text(\"Availability\")').text_content()}")
        print(f"\nProduct {product_details.locator('p:has-text(\"Condition\")').text_content()}")
        print(f"\nProduct {product_details.locator('p:has-text(\"Brand\")').text_content()}")
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/FirstProductDetails_{ts}.png")

    def get_searched_product_details(self, get_data, snap_dir, log):
        '''
        Search and capture product details
        '''
        self.page.locator("#search_product").fill(f"{get_data['SEARCHED_PRODUCT']}")
        common_lib.debug_print(log, "INFO", f"Searched product name: {get_data['SEARCHED_PRODUCT']}")
        self.page.locator("#submit_search").click()
        common_lib.debug_print(log, "INFO", "Submit search clicked")
        expect(self.page.get_by_text("Searched Products")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Searched Products text visible")
        searched_products = self.page.locator(".features_items .col-sm-4")
        try:
            product_count = searched_products.count()
        except Exception:
            common_lib.debug_print(log, "WARNING", "No such product available...")
            product_count = 0
        common_lib.debug_print(log, "INFO", f"Total searched product count : {product_count}")
        assert product_count > 0, "No searched products found"
        for i in range(0, product_count, 3):
            searched_products.nth(i).scroll_into_view_if_needed()
            expect(searched_products.nth(i)).to_be_visible()
            common_lib.debug_print(log, "INFO", f"visible product: {searched_products.nth(i)}")
            ts = common_lib.time_extension()
            self.page.screenshot(path=f"{snap_dir}/FirstProductDetails_{ts}.png")

    def add_product_to_cart(self, snap_dir, product_count, log):
        '''
        Add products to cart
        '''
        for i in range(product_count):
            product = self.page.locator(".features_items .col-sm-4").nth(i)
            product.scroll_into_view_if_needed()
            product.hover()
            product.locator("div.overlay-content a:has-text('Add to cart')").click()
            common_lib.debug_print(log, "INFO", "Add to cart clicked")
            time.sleep(0.5)
            ts = common_lib.time_extension()
            self.page.screenshot(path=f"{snap_dir}/AddProduct_{ts}.png")
            if i < product_count-1:
                self.page.locator("button:has-text('Continue Shopping')").click()
                common_lib.debug_print(log, "INFO", "Continue Shopping clicked")
            elif i == product_count-1:
                self.page.locator("u:has-text('View Cart')").click()
                common_lib.debug_print(log, "INFO", "View cart clicked")
        try:
            cart_product_count = self.page.locator("table.table.table-condensed tbody tr").count()
        except Exception:
            common_lib.debug_print(log, "WARNING", "No product available in cart...")
            cart_product_count = 0
        common_lib.debug_print(log, "INFO", f"Total cart product count : {cart_product_count}")
        assert cart_product_count == product_count, "WARNING: Cart product count mismatch"

    def get_cart_details(self, snap_dir, product_count, log):
        '''
        Retrieve cart details
        '''
        cart_rows = self.page.locator("table.table.table-condensed tbody tr")
        for i in range(product_count):
            item = cart_rows.nth(i)
            price = item.locator("td.cart_price").text_content()
            quantity = item.locator("td.cart_quantity").text_content()
            total = item.locator("td.cart_total").text_content()
            details = f"\nProduct {i+1} - Price: {price.strip()}, Quantity: {quantity.strip()}, Total: {total.strip()}"
            common_lib.debug_print(log, "INFO", f"{details}")
            assert price is not None and "Rs." in price, "WARNING: price details not available"
            assert quantity.strip().isdigit(), "WARNING: Quantity = 0"
            assert total is not None and "Rs." in total, "WARNING: Total price details not available"
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/GetCartDetails_{ts}.png")

    def cart_checkout(self, get_data, snap_dir, log):
        '''
        Checkout process
        '''
        # Proceed to checkout and validate address details
        self.page.get_by_text("Proceed To Checkout").click()
        common_lib.debug_print(log, "INFO", "Proceed To Checkout clicked")
        expect(self.page.get_by_text("Checkout")).to_be_visible()
        expect(self.page.get_by_role("heading", name="Address Details")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Address Details and Checkout text visible")

        # Ensure mobile number element is in view (if present)
        try:
            self.page.locator("#address_invoice").get_by_text(f"{get_data['FORMS_DATA']['MOBILE_NUMBER']}").scroll_into_view_if_needed()
        except Exception:
            # element may not be present; continue
            pass

        delivery_address = self.page.locator("//*[@id='address_delivery']").inner_text()
        common_lib.debug_print(log, "INFO", f"Delivery Address Details: \n\t{delivery_address}\n")
        invoice_address = self.page.locator("//*[@id='address_invoice']").inner_text()
        common_lib.debug_print(log, "INFO", f"Billing Address Details: \n\t{invoice_address}\n")

        full_name = f"{get_data['FORMS_DATA'].get('GENDER','')} {get_data['FORMS_DATA'].get('FIRST_NAME','')} {get_data['FORMS_DATA'].get('LAST_NAME','')}".strip()
        state_address = f"{get_data['FORMS_DATA'].get('CITY','')} {get_data['FORMS_DATA'].get('STATE','')} {get_data['FORMS_DATA'].get('ZIP_CODE','')}".strip()

        # Delivery address assertions
        assert full_name in delivery_address, "WARNING: Name mismatch in delivery_address"
        assert f"{get_data['FORMS_DATA'].get('COMPANY','')}" in delivery_address, "WARNING: Company mismatch in delivery_address"
        assert f"{get_data['FORMS_DATA'].get('ADDRESS_1','')}" in delivery_address, "WARNING: Address_1 mismatch in delivery_address"
        assert f"{get_data['FORMS_DATA'].get('ADDRESS_2','')}" in delivery_address, "WARNING: Address_2 mismatch in delivery_address"
        assert state_address in delivery_address, "WARNING: state_address mismatch in delivery_address"
        assert f"{get_data['FORMS_DATA'].get('COUNTRY','')}" in delivery_address, "WARNING: Country mismatch in delivery_address"
        assert f"{get_data['FORMS_DATA'].get('MOBILE_NUMBER','')}" in delivery_address, "WARNING: Mobile number mismatch in delivery_address"

        # Invoice address assertions
        assert full_name in invoice_address, "WARNING: Name mismatch in invoice_address"
        assert f"{get_data['FORMS_DATA'].get('COMPANY','')}" in invoice_address, "WARNING: Company mismatch in invoice_address"
        assert f"{get_data['FORMS_DATA'].get('ADDRESS_1','')}" in invoice_address, "WARNING: Address_1 mismatch in invoice_address"
        assert f"{get_data['FORMS_DATA'].get('ADDRESS_2','')}" in invoice_address, "WARNING: Address_2 mismatch in invoice_address"
        assert state_address in invoice_address, "WARNING: state_address mismatch in invoice_address"
        assert f"{get_data['FORMS_DATA'].get('COUNTRY','')}" in invoice_address, "WARNING: Country mismatch in invoice_address"
        assert f"{get_data['FORMS_DATA'].get('MOBILE_NUMBER','')}" in invoice_address, "WARNING: Mobile number mismatch in invoice_address"

        # Screenshot and add order message
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/GetCartDetails_{ts}.png")
        self.page.locator("#cart_items").click()
        self.page.locator("textarea[name='message']").scroll_into_view_if_needed()
        self.page.locator("textarea[name='message']").fill("This is Home Address")
        common_lib.debug_print(log, "INFO", "Type data: This is Home Address")
        self.page.get_by_role("link", name="Place Order").click()
        common_lib.debug_print(log, "INFO", "Place Order clicked")
