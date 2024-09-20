"""
Read the test settings, if the file does not exist, an empty one will be created.
"""

import json
import os


class TestSettings:

    _FILENAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "test_settings.json"))

    @classmethod
    def _create_defaults(cls):
        defaults = {
            "serial_port": ""
        }
        with open(cls._FILENAME, "w") as fp:
            json.dump(defaults, fp, indent=4)

    @classmethod
    def _read_setting(cls, parameter):
        if not os.path.isfile(cls._FILENAME):
            cls._create_defaults()
        with open(cls._FILENAME, "r") as fp:
            settings = json.load(fp)
        return settings.get(parameter, None)

    @classmethod
    def get_serial_port(cls):
        return cls._read_setting("serial_port")


if __name__ == "__main__":

    print("Serial port:", TestSettings.get_serial_port())
