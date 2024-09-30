"""
Run all the tests for the models.
"""


from lily_unit_test import TestRunner

from unit_tests.test_runner_settings import TestRunnerSettings


TestRunner.run(TestRunnerSettings.get_test_suites_path("firmware"),
               TestRunnerSettings.get_test_options())
