# account_page.py
import json
import time
from utilities import common_lib
from playwright.sync_api import Page, expect


class AccountPage:
    """
    Account page automation using Playwright
    """

    def __init__(self, page: Page):
        self.page = page

    def go_to(self, url: str, log: str):
        """
        Redirect to a URL and log the action.
        """
        self.page.goto(url)
        common_lib.debug_print(log, "INFO", f"Redirecting to url: {url}")

    def page_scroll(self):
        """
        Scroll the page to its full size.
        """
        full_height = self.page.evaluate("() => document.body.scrollHeight")
        full_width = self.page.evaluate("() => document.body.scrollWidth")
        print(f"Full page size: {full_height}px x {full_width}px")
        self.page.evaluate(f"window.scrollTo({full_height},{full_width})")

    def remove_ads(self):
        """
        Remove common ad elements from the page DOM.
        """
        self.page.evaluate("""
        () => {
            const ads = document.querySelectorAll("iframe, ins, div[id*='ad'], div[class*='ad']");
            ads.forEach(ad => ad.remove());
        }
        """)

    def handle_ads_if_present(self, log: str):
        """
        Attempt to close or remove floating ads if present.
        """
        try:
            ad_locator = self.page.locator("iframe, div[style*='position: fixed']")
            count = ad_locator.count()
            if count > 0:
                for i in range(count):
                    try:
                        ad = ad_locator.nth(i)
                        if ad.is_visible():
                            close_btn = ad.locator("button, span, [aria-label='close']")
                            if close_btn.count() > 0 and close_btn.first.is_visible():
                                close_btn.first.click()
                            else:
                                # Fallback: remove the ad element
                                self.page.evaluate("(el) => el.remove()", ad)
                    except Exception as e:
                        common_lib.debug_print(log, "WARNING", f"Exception occured while removing ads: {e}")
        except Exception as e:
            common_lib.debug_print(log, "WARNING", f"Error locating ads: {e}")

    def sign_up(self, get_data: dict, snap_dir: str, log: str):
        """
        Navigate to signup/login, verify elements, fill initial signup fields, and click Signup.
        """
        self.handle_ads_if_present(log)
        self.page.get_by_role("link", name="Signup / Login").click()
        common_lib.debug_print(log, "INFO", f"Page Title: {self.page.title()}")
        expect(self.page.get_by_text("New User Signup!")).to_be_visible()
        common_lib.debug_print(log, "INFO", "New User Signup text visible")
        expect(self.page.get_by_role("button", name="Signup")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Signup Button visible")

        self.page.get_by_placeholder("Name").type(f"{get_data['FORMS_DATA']['FULL_NAME']}")
        common_lib.debug_print(log, "INFO", f"Type Name: {get_data['FORMS_DATA']['FULL_NAME']}")
        self.page.locator("[data-qa='signup-email']").type(f"{get_data['FORMS_DATA']['EMAIL_ID']}")
        common_lib.debug_print(log, "INFO", f"Type Sign-up Email-ID: {get_data['FORMS_DATA']['EMAIL_ID']}")

        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/AccountTest_{ts}.png")
        self.page.get_by_role("button", name="Signup").click()
        common_lib.debug_print(log, "INFO", "Signup button clicked")

    def fill_signup_forms(self, get_data: dict, snap_dir: str, log: str):
        """
        Fill the signup form fields, validate prefilled values, and submit the form.
        """
        self.handle_ads_if_present(log)
        expect(self.page.get_by_text("Enter Account Information")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Enter Account Information text visible")

        # Gender selection
        self.page.locator(f"xpath=//*[@value='{get_data['FORMS_DATA']['GENDER']}']").click()

        # Validate full name
        data = self.page.locator("xpath=//*[@id='name']").get_attribute("value")
        common_lib.debug_print(log, "INFO", f"Full Name shown = {data}")
        assert data == f"{get_data['FORMS_DATA']['FULL_NAME']}", "WARNING: Name Details mismatch"

        # Email field may be disabled and prefilled
        if self.page.locator("xpath=//*[@id='email']").is_disabled():
            common_lib.debug_print(log, "INFO", "Email ID text area disabled")
            email = self.page.locator("xpath=//*[@id='email']").get_attribute("value")
            common_lib.debug_print(log, "INFO", f"Email ID text area disabled and value : {email}")
            assert email == f"{get_data['FORMS_DATA']['EMAIL_ID']}", "WARNING: Email-ID mismatch"

        # Password and DOB
        self.page.locator("xpath=//*[@id='password']").scroll_into_view_if_needed()
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/AccountTest_{ts}.png")
        self.page.locator("xpath=//*[@id='password']").type(f"{get_data['FORMS_DATA']['PASSWORD']}")
        self.page.select_option("#days", label=f"{get_data['FORMS_DATA']['DOB']}")
        self.page.select_option("#months", label=f"{get_data['FORMS_DATA']['MOB']}")
        self.page.select_option("#years", label=f"{get_data['FORMS_DATA']['YOB']}")

        # Newsletter and offers
        self.page.select_option("#years", label=f"{get_data['FORMS_DATA']['YOB']}")
        self.page.locator("xpath=//*[@id='newsletter']").click()
        self.page.locator("xpath=//*[@id='optin']").click()
        common_lib.debug_print(log, "INFO", "Checked newsletter and optin")
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/AccountTest_{ts}.png")

        # Address information
        self.page.locator("xpath=//*[@id='company']").scroll_into_view_if_needed()
        expect(self.page.get_by_text("Address Information")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Address Information text visible")

        self.page.locator("xpath=//*[@id='first_name']").type(f"{get_data['FORMS_DATA']['FIRST_NAME']}")
        self.page.locator("xpath=//*[@id='last_name']").type(f"{get_data['FORMS_DATA']['LAST_NAME']}")
        self.page.locator("xpath=//*[@id='company']").type(f"{get_data['FORMS_DATA']['COMPANY']}")
        self.page.locator("xpath=//*[@id='address1']").type(f"{get_data['FORMS_DATA']['ADDRESS_1']}")
        self.page.locator("xpath=//*[@id='address2']").type(f"{get_data['FORMS_DATA']['ADDRESS_2']}")
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/AccountTest_{ts}.png")

        self.page.locator("xpath=//*[@id='zipcode']").scroll_into_view_if_needed()
        self.page.select_option("#country", label=f"{get_data['FORMS_DATA']['COUNTRY']}")
        self.page.locator("xpath=//*[@id='state']").type(f"{get_data['FORMS_DATA']['STATE']}")
        self.page.locator("xpath=//*[@id='city']").type(f"{get_data['FORMS_DATA']['CITY']}")
        self.page.locator("xpath=//*[@id='zipcode']").type(f"{get_data['FORMS_DATA']['ZIP_CODE']}")
        self.page.locator("xpath=//*[@id='mobile_number']").type(f"{get_data['FORMS_DATA']['MOBILE_NUMBER']}")

        forms_data = json.dumps(get_data['FORMS_DATA'], indent=4)
        common_lib.debug_print(log, "INFO", f"FORMS_DATA: {forms_data}")
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/AccountTest_{ts}.png")

        # Submit and verify
        self.page.get_by_role("button", name="Create Account").click()
        common_lib.debug_print(log, "INFO", "Create Account clicked")
        expect(self.page.get_by_text("Account Created")).to_be_visible()
        expect(self.page.get_by_text("successfully created")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Successfully Account created text visible")
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/AccountTest_{ts}.png")
        self.page.get_by_role("link", name="Continue").click()
        common_lib.debug_print(log, "INFO", "Continue button clicked")

    def logout_account(self, snap_dir: str, log: str):
        """
        Logout the current account.
        """
        expect(self.page.locator("//a[text()=' Logout']")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Logout Hover visible")
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/AccountTest_{ts}.png")
        self.page.locator("//a[text()=' Logout']").click()
        common_lib.debug_print(log, "INFO", "Logout button clicked")

    def delete_account(self, snap_dir: str, log: str):
        """
        Initiate account deletion flow.
        """
        self.handle_ads_if_present(log)
        expect(self.page.locator("//a[text()=' Delete Account']")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Delete Account Hover visible")
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/AccountTest_{ts}.png")
        self.page.locator("//a[text()=' Delete Account']").click()
        common_lib.debug_print(log, "INFO", "Delete Account button clicked")

    def delete_account_confirmation(self, snap_dir: str, log: str):
        """
        Confirm account deletion and proceed.
        """
        self.handle_ads_if_present(log)
        expect(self.page.get_by_text("Account Deleted!")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Account Deleted text visible")
        expect(self.page.get_by_text("permanently deleted")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Permanently deleted text visible")
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/AccountTest_{ts}.png")
        self.page.get_by_role("link", name="Continue").click(force=True)
        common_lib.debug_print(log, "INFO", "Continue button clicked")

    def existing_account_check(self, get_data: dict, snap_dir: str, log: str):
        """
        Verify that an account already exists for the provided email.
        """
        self.page.get_by_role("link", name="Signup / Login").click()
        common_lib.debug_print(log, "INFO", "Signup / Login button clicked")
        self.page.get_by_placeholder("Name").type(f"{get_data['FORMS_DATA']['FULL_NAME']}")
        common_lib.debug_print(log, "INFO", f"Type Full name: {get_data['FORMS_DATA']['FULL_NAME']}")
        self.page.locator("[data-qa='signup-email']").type(f"{get_data['FORMS_DATA']['EMAIL_ID']}")
        common_lib.debug_print(log, "INFO", f"Type signup email: {get_data['FORMS_DATA']['EMAIL_ID']}")
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/AccountTest_{ts}.png")
        self.page.get_by_role("button", name="Signup").click()
        common_lib.debug_print(log, "INFO", "Signup button clicked")
        expect(self.page.get_by_text("Email Address already exist")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Email Address already exist text visible")
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/AccountTest_{ts}.png")

    def invalid_login_check(self, get_data: dict, snap_dir: str, log: str):
        """
        Attempt login with invalid credentials and verify error message.
        """
        self.page.get_by_role("link", name="Signup / Login").click()
        common_lib.debug_print(log, "INFO", "Signup / Login button clicked")
        expect(self.page.get_by_text("Login to your account")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Login to your account text visible")
        expect(self.page.get_by_role("button", name="Login")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Login Button visible")

        self.page.locator("[data-qa='login-email']").fill(get_data["INVALID_LOGIN_DATA"]["EMAIL_ID"])
        common_lib.debug_print(log, "INFO", "Type Invalid login email: " + f"{get_data['INVALID_LOGIN_DATA']['EMAIL_ID']}")
        self.page.locator("[data-qa='login-password']").fill(get_data["INVALID_LOGIN_DATA"]["PASSWORD"])
        common_lib.debug_print(log, "INFO", "Type Invalid login password: " + f"{get_data['INVALID_LOGIN_DATA']['PASSWORD']}")

        self.page.get_by_role("button", name="Login").click()
        common_lib.debug_print(log, "INFO", "Login button clicked")
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/AccountTest_{ts}.png")
        expect(self.page.get_by_text("Your email or password is incorrect")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Your email or password is incorrect text visible")

    def valid_login_check(self, get_data: dict, snap_dir: str, log: str):
        """
        Login with valid credentials and verify successful login.
        """
        self.page.get_by_role("link", name="Signup / Login").click()
        common_lib.debug_print(log, "INFO", "Signup / Login button clicked")
        expect(self.page.get_by_text("Login to your account")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Login to your account text visible")
        expect(self.page.get_by_role("button", name="Login")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Login button visible")

        self.page.locator("[data-qa='login-email']").fill(get_data["FORMS_DATA"]["EMAIL_ID"])
        common_lib.debug_print(log, "INFO", "Type valid login email: " + f"{get_data['FORMS_DATA']['EMAIL_ID']}")
        self.page.locator("[data-qa='login-password']").fill(get_data["FORMS_DATA"]["PASSWORD"])
        common_lib.debug_print(log, "INFO", "Type valid login password: " + f"{get_data['FORMS_DATA']['PASSWORD']}")

        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/AccountTest_{ts}.png")
        self.page.get_by_role("button", name="Login").click()
        common_lib.debug_print(log, "INFO", "Login button clicked")

        expect(self.page.get_by_text(f"Logged in as {get_data['FORMS_DATA']['FIRST_NAME']} {get_data['FORMS_DATA']['LAST_NAME']}")).to_be_visible()
        common_lib.debug_print(log, "INFO", "Logged in as " + f"{get_data['FORMS_DATA']['FIRST_NAME']} {get_data['FORMS_DATA']['LAST_NAME']}")
