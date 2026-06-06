import json
import time
from utilities import common_lib
from playwright.sync_api import expect

class ContactPage:
    def __init__(self, page):
        self.page = page

    def go_to(self, url: str, log: str):
        """
        Navigate to a given URL and log the action
        """
        self.page.goto(url)
        common_lib.debug_print(log, "INFO", f"Redirecting to url: {url}")

    def fill_contact_details(self, get_data, snap_dir, log):
        """
        Fill out the contact form with provided data, upload a file,
        log actions, and take a screenshot.
        """
        self.page.get_by_role("link", name="Contact").click()
        expect(
            self.page.get_by_text("Note: Below contact form is for testing purpose.")
        ).to_be_visible()
        common_lib.debug_print(log, "INFO", "Contact form note is visible")

        self.page.locator("[data-qa='name']").fill(get_data['CONTACT_DETAILS']['NAME'])
        self.page.locator("[data-qa='email']").fill(get_data['CONTACT_DETAILS']['EMAIL_ID'])
        self.page.locator("[data-qa='subject']").fill(get_data['CONTACT_DETAILS']['SUBJECT'])
        self.page.locator("[data-qa='message']").fill(get_data['CONTACT_DETAILS']['MESSAGE'])

        self.page.set_input_files("input[name='upload_file']", "./data/sample.txt")

        contact_data = json.dumps(get_data['CONTACT_DETAILS'], indent=4)
        common_lib.debug_print(log, "INFO", f"Filled data for contact:\n{contact_data}")
        common_lib.debug_print(log, "INFO", "Uploaded file ./data/sample.txt")

        time_stamp = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/Contact_{time_stamp}.png")

    def get_alert_confirmation(self, snap_dir, log):
        """
        Handle alert confirmation after form submission,
        log success, and take screenshots.
        """
        self.page.on("dialog", lambda dialog: print(dialog.message))
        self.page.on("dialog", lambda dialog: dialog.accept())
        self.page.click('input[data-qa="submit-button"]')

        time.sleep(1)
        time_stamp = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/Contact_{time_stamp}.png")

        assert self.page.is_visible(
            'div.status.alert.alert-success:has-text("Success! Your details have been submitted successfully.")'
        )
        common_lib.debug_print(log, "INFO", "Success alert is visible")

        time_stamp = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/Contact_{time_stamp}.png")


# Example usage
if __name__ == "__main__":
    print("ContactPage class with go_to, fill_contact_details, and get_alert_confirmation is ready.")
