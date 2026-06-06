from utilities import common_lib
from src import instance_page
import pytest

class TestInstance:
    '''
    Test Instance class to execute test
    '''

    @pytest.mark.webtest
    def test_instance_check(self, create_page_instance):
        '''
        Instances add, delete
        '''
        snap_dir = common_lib.create_directory("artifacts/screenshot", "test_instance_check")
        f_name = common_lib.create_log_file("instance")
        get_data = common_lib.read_credentials()
        page = create_page_instance
        instance_obj = instance_page.InstancePage(page)

        # Navigation and chart checks
        instance_obj.go_to(f"{get_data['INSTANCE_URL']}", f_name)
        instance_obj.navigation_tabs(snap_dir, f_name)
        instance_obj.get_chart_data(snap_dir, f_name, "cpuChart")
        instance_obj.get_chart_data(snap_dir, f_name, "storageChart")
        instance_obj.get_chart_data(snap_dir, f_name, "networkChart")

        # Instance lifecycle
        instance_obj.instance_creation(get_data, snap_dir, f_name)
        instance_obj.instance_filtering(get_data, snap_dir, f_name)
        instance_obj.instance_creation_confirmation(get_data, snap_dir, f_name)
        instance_obj.instance_deletion(get_data, snap_dir, f_name)
