"""
Test CRC8 model.
"""

import lily_unit_test

from application.models.crc8 import calculate_crc


class TestCrc8(lily_unit_test.TestSuite):

    def test_get_module_id(self):
        data = [76, 105, 108, 121, 84, 114, 111, 110, 105, 99, 115]
        crcs = [227, 191, 55, 237, 38, 171, 82, 180, 29, 125, 42]
        for i in range(1, len(data) + 1):
            crc = calculate_crc(data[:i])
            self.fail_if(crc != crcs[i - 1], f"Wrong CRC: {crc}, expected: {crcs[i - 1]}")


if __name__ == "__main__":

    TestCrc8().run()
