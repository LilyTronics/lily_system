"""
Setting for all the test runners.
"""

import os


class TestRunnerSettings:

    @staticmethod
    def get_test_suites_path(subfolder_name):
        return os.path.join(os.path.dirname(__file__), subfolder_name)

    @staticmethod
    def get_test_options():
        return {
            "report_folder": os.path.join(os.path.dirname(__file__), "test_reports"),
            "create_html_report": True,
            "open_in_browser": True,
            "no_log_files": True
        }


if __name__ == "__main__":

    print("Test suites path:", TestRunnerSettings.get_test_suites_path("test_suites"))
    print("Test options    :", TestRunnerSettings.get_test_options())
