# instance_page.py
import json
import time
from utilities import common_lib
from playwright.sync_api import Page, expect


class InstancePage:
    """
    Instance page automation and utilities
    """

    def __init__(self, page: Page):
        self.page = page

    def go_to(self, url: str, log: str):
        """
        Navigate to a given URL and log the action
        """
        self.page.goto(url)
        common_lib.debug_print(log, "INFO", f"Redirecting to url: {url}")

    def navigation_tabs(self, snap_dir: str, log: str):
        """
        Hover and click through main navigation tabs, then open Instances.
        """
        nav_list = [
            "Library", "Operations", "Infrastructure",
            "Backups", "Tools", "Administration", "Provisioning"
        ]
        for tab in nav_list:
            self.page.hover(f"text={tab}", timeout=1000)
            common_lib.debug_print(log, "INFO", f"Hovering {tab}")
            self.page.click(f"text={tab}", timeout=1000)
            common_lib.debug_print(log, "INFO", f"Clicked on: {tab}")

        self.page.click("text=Instances", timeout=1000)
        common_lib.debug_print(log, "INFO", "Clicked on: Instances")
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/InstanceTest_{ts}.png")

    def get_chart_data(self, snap_dir: str, log: str, chart_type: str):
        """
        Extract chart labels and datasets by evaluating JS in the page context.
        """
        chart_data = self.page.evaluate(
            """(chart_type) => {
                const chart = Chart.getChart(chart_type);
                if (!chart) return 'Chart not initialized';
                return { labels: chart.data.labels, values: chart.data.datasets };
            }""",
            chart_type
        )

        common_lib.debug_print(log, "INFO", f"{chart_type} data = {chart_data}")

        if isinstance(chart_data, str):
            common_lib.debug_print(log, "WARNING", f"{chart_type} -> {chart_data}")
            ts = common_lib.time_extension()
            self.page.screenshot(path=f"{snap_dir}/InstanceTest_{ts}.png")
            return chart_data

        if "cpu" in chart_type:
            common_lib.debug_print(log, "INFO", "getting data of " + f"{chart_data['values'][0]['label']}")
        elif "network" in chart_type:
            common_lib.debug_print(log, "INFO", "getting data of " + f"{chart_data['values'][0]['label']}")
        else:
            pass

        for i in range(len(chart_data['labels'])):
            common_lib.debug_print(
                log,
                "INFO",
                f"{chart_data['labels'][i]} : {chart_data['values'][0]['data'][i]}"
            )

        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/InstanceTest_{ts}.png")
        return chart_data

    def instance_creation(self, get_data: dict, snap_dir: str, log: str):
        """
        Create instances based on VM_DETAILS in get_data.
        """
        for i in range(len(get_data['VM_DETAILS'])):
            self.page.get_by_role("button", name="Add").click()
            common_lib.debug_print(log, "INFO", "Clicked on: Add Button")
            expect(self.page.get_by_text("CREATE INSTANCE")).to_be_visible()
            common_lib.debug_print(log, "INFO", "CREATE INSTANCE is visible")

            self.page.get_by_role("radio", name=f"Create {get_data['VM_DETAILS'][i]['VM_NAME']}").click()
            common_lib.debug_print(log, "INFO", "Selected VM: " + f"{get_data['VM_DETAILS'][i]['VM_NAME']}")

            self.page.select_option("#groupSelect", label=f"{get_data['VM_DETAILS'][i]['GROUP']}")
            common_lib.debug_print(log, "INFO", "Selected group: " + f"{get_data['VM_DETAILS'][i]['GROUP']}")

            self.page.select_option("#cloudSelect", label=f"{get_data['VM_DETAILS'][i]['CLOUD']}")
            common_lib.debug_print(log, "INFO", "Selected cloud: " + f"{get_data['VM_DETAILS'][i]['CLOUD']}")

            self.page.select_option("#statusSelect", label=f"{get_data['VM_DETAILS'][i]['STATUS']}")
            common_lib.debug_print(log, "INFO", "Selected status: " + f"{get_data['VM_DETAILS'][i]['STATUS']}")

        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/InstanceTest_{ts}.png")
        self.page.get_by_role("button", name="OK").click()
        common_lib.debug_print(log, "INFO", "Clicked on OK button")

    def instance_creation_confirmation(self, get_data: dict, snap_dir: str, log: str):
        """
        Verify created instances are visible with expected details.
        """
        try:
            status_count = self.page.get_by_text(f"Status: {get_data['INSTANCE_FILTER']['STATUS']}").count()
        except Exception:
            common_lib.debug_print(log, "INFO", "In instance_creation_confirmation method :- ")
            common_lib.debug_print(log, "WARNING", f"Status: {get_data['INSTANCE_FILTER']['STATUS']} not found...")
            status_count = 0

        if status_count > 0:
            for i in range(status_count):
                common_lib.debug_print(log, "INFO", "Group: " + f"{get_data['VM_DETAILS'][i]['GROUP']} visible")
                expect(self.page.get_by_text(f"Cloud: {get_data['VM_DETAILS'][i]['CLOUD']}").nth(i)).to_be_visible()
                common_lib.debug_print(log, "INFO", "Cloud: " + f"{get_data['VM_DETAILS'][i]['CLOUD']} visible")
                expect(self.page.get_by_text(f"Status: {get_data['VM_DETAILS'][i]['STATUS']}").nth(i)).to_be_visible()
                common_lib.debug_print(log, "INFO", "Status: " + f"{get_data['VM_DETAILS'][i]['STATUS']} visible")
                expect(self.page.get_by_role("button", name="DELETE").nth(i)).to_be_visible()
                common_lib.debug_print(log, "INFO", f"DELETE Button visible position: {i}")
                ts = common_lib.time_extension()
                self.page.screenshot(path=f"{snap_dir}/InstanceTest_{ts}.png")

    def instance_filtering(self, get_data: dict, snap_dir: str, log: str):
        """
        Apply filters (search, group, cloud, status) and capture matching instances.
        """
        common_lib.debug_print(log, "INFO", f"{get_data['INSTANCE_FILTER']['SEARCH_TEXT']}")

        self.page.select_option("#filterGroup", label=f"{get_data['INSTANCE_FILTER']['GROUP']}")
        common_lib.debug_print(log, "INFO", f"Filter group: {get_data['INSTANCE_FILTER']['GROUP']}")

        self.page.select_option("#filterCloud", label=f"{get_data['INSTANCE_FILTER']['CLOUD']}")
        common_lib.debug_print(log, "INFO", f"Filter cloud: {get_data['INSTANCE_FILTER']['CLOUD']}")

        self.page.select_option("#filterStatus", label=f"{get_data['INSTANCE_FILTER']['STATUS']}")
        common_lib.debug_print(log, "INFO", f"Filter status: {get_data['INSTANCE_FILTER']['STATUS']}")

        try:
            status_count = self.page.get_by_text(f"Status: {get_data['INSTANCE_FILTER']['STATUS']}").count()
        except Exception:
            common_lib.debug_print(log, "INFO", "In instance_filtering method :- ")
            common_lib.debug_print(log, "WARNING", f"Status: {get_data['INSTANCE_FILTER']['STATUS']} not found...")
            status_count = 0

        common_lib.debug_print(log, "INFO", f"Instance Filtering status count = {status_count}")

        if status_count > 0:
            for i in range(status_count):
                self.page.get_by_role("button", name="DELETE").nth(i).scroll_into_view_if_needed()
                common_lib.debug_print(log, "INFO", f"Scroll to DELETE button position: {i}")
                ts = common_lib.time_extension()
                self.page.screenshot(path=f"{snap_dir}/InstanceTest_{ts}.png")

    def instance_deletion(self, get_data: dict, snap_dir: str, log: str):
        """
        Delete instances matching the filter status.
        """
        try:
            status_count = self.page.get_by_text(f"Status: {get_data['INSTANCE_FILTER']['STATUS']}").count()
        except Exception:
            common_lib.debug_print(log, "INFO", "In instance_deletion method :- ")
            common_lib.debug_print(log, "WARNING", f"Status: {get_data['INSTANCE_FILTER']['STATUS']} not found...")
            status_count = 0

        common_lib.debug_print(log, "INFO", f"Instance_Deletion status count = {status_count}")

        if status_count > 0:
            for i in range(status_count):
                self.page.get_by_role("button", name="DELETE").nth(i).scroll_into_view_if_needed()
                common_lib.debug_print(log, "INFO", f"Scroll to DELETE button position: {i}")
                expect(self.page.get_by_role("button", name="DELETE").nth(i)).to_be_visible()
                common_lib.debug_print(log, "INFO", f"Visible DELETE button position: {i}")
                ts = common_lib.time_extension()
                self.page.screenshot(path=f"{snap_dir}/InstanceTest_{ts}.png")
                self.page.get_by_role("button", name="DELETE").nth(i).click()
                common_lib.debug_print(log, "INFO", f"Clicked to DELETE button position: {i}")
                expect(self.page.get_by_text(f"Status: {get_data['INSTANCE_FILTER']['STATUS']}")).not_to_be_visible()

        common_lib.debug_print(log, "INFO", "DELETE button not visible position")
        common_lib.debug_print(log, "INFO", "In instance_deletion method :- ")
        common_lib.debug_print(log, "INFO", "SUCCESS", f"Status: {get_data['INSTANCE_FILTER']['STATUS']} not visible...")
        ts = common_lib.time_extension()
        self.page.screenshot(path=f"{snap_dir}/InstanceTest_{ts}.png")
