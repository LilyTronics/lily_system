"""
Test data packet model.
"""

import lily_unit_test

from application.models.crc8 import calculate_crc
from application.models.data_packet import DataPacket


class TestDataPacket(lily_unit_test.TestSuite):

    # Packet is valid when:
    # 1 <= DSN <= 255
    # 0 <= SSN <= 255
    # DSN != SSN
    # 1 <= PID <= 65535
    # 1 <= len(data) <= 35
    # Invalid packets do not generate any data: get_data() should return an empty array

    def test_empty_data_packet(self):
        packet = DataPacket()
        data = packet.get_data()
        self.fail_if(len(data) > 0, f"There is data while there should not be data: {data}")

    def test_dsn(self):
        packet = DataPacket()
        packet.ssn = 1
        packet.pid = 1
        packet.data = [1]
        # Invalid DSN
        for test_dsn in [0, 256, packet.ssn]:
            packet.dsn = test_dsn
            data = packet.get_data()
            self.fail_if(len(data) > 0, f"Data generated when DSN = {test_dsn}: {data}")
        # Valid DSN
        packet.dsn = 3
        data = packet.get_data()
        self.fail_if(data != b"\x02\x03\x01\x00\x01\x01\xa2\x04",
                     f"Invalid data generated when DSN = 3: {data}")

    def test_ssn(self):
        packet = DataPacket()
        packet.dsn = 1
        packet.pid = 1
        packet.data = [1]
        # Invalid SSN
        for test_ssn in [-1, 256, packet.dsn]:
            packet.ssn = test_ssn
            data = packet.get_data()
            self.fail_if(len(data) > 0, f"Data generated when SSN = {test_ssn}: {data}")
        # Valid SSN
        packet.ssn = 3
        data = packet.get_data()
        self.fail_if(data != b"\x02\x01\x03\x00\x01\x01J\x04",
                     f"Invalid data generated when SSN = 3: {data}")

    def test_pid(self):
        packet = DataPacket()
        packet.dsn = 1
        packet.ssn = 2
        packet.data = [1]
        # Invalid PID
        for test_pid in [-1, 65536]:
            packet.pid = test_pid
            data = packet.get_data()
            self.fail_if(len(data) > 0, f"Data generated when PID = {test_pid}: {data}")
        # Valid PID
        packet.pid = 1148
        data = packet.get_data()
        self.fail_if(data != b"\x02\x01 \xfd \xfb|\x01\xbc\x04",
                     f"Invalid data generated when PID = 1148: {data}")

    def test_data(self):
        packet = DataPacket()
        packet.dsn = 1
        packet.ssn = 2
        packet.pid = 1
        packet.data = []
        data = packet.get_data()
        self.fail_if(len(data) > 0, f"Data generated when data length = 0: {data}")
        data = packet.get_data()
        self.fail_if(len(data) > 0, f"Data generated when data length = 36: {data}")
        packet.data = [1]
        data = packet.get_data()
        self.fail_if(data != b"\x02\x01 \xfd\x00\x01\x01\\\x04",
                     f"Invalid data generated when data = [1]: {data}")

    def test_byte_stuffing(self):
        packet = DataPacket()
        packet.dsn = 1
        packet.ssn = 3
        packet.pid = 1
        packet.data = [1]
        # No stuffing
        data = packet.get_data()
        self.fail_if(packet.DLE in data, "DLE found in data when not expected")
        # With stuffing
        packet.data = [packet.STX, packet.ETX, packet.DLE]
        data = packet.get_data()
        dle_count = data.count(packet.DLE)
        self.fail_if(dle_count != 3, f"Expected 3 occurrences of DLE, found: {dle_count}")
        pos = 0
        for i, special_byte in enumerate([packet.STX, packet.ETX, packet.DLE]):
            pos = data.find(packet.DLE, pos)
            if pos >= 0:
                unstuffed_byte = ~data[pos + 1] & 0xFF
                self.fail_if(unstuffed_byte != special_byte,
                             f"Special byte {special_byte} not found, found: {unstuffed_byte}")
            pos += 1

    def test_crc(self):
        packet = DataPacket()
        packet.dsn = 1
        packet.ssn = 3
        packet.pid = 5
        packet.data = [1]
        data = packet.get_data()
        crc = calculate_crc(data[1:-2])
        self.fail_if(crc != data[-2], f"Invalid CR found: {data[2]}, expected: {crc}")

    def test_numeric_conversion(self):
        test_data = [212, 112, 34, 141, 131, 138, 202, 4]
        expected_values_unsigned = [212, 54384, 13922338, 3564118669, 912414379395,
                                    233578081125258, 59795988768066250, 15307773124624960004]
        expected_values_signed = [-44, -11152, -2854878, -730848627, -187097248381,
                                  -47896895585398, -12261605269861686, -3138970949084591612]

        packet = DataPacket()
        packet.dsn = 1
        packet.ssn = 0
        packet.pid = 1
        # Max number of bytes for conversion is 8
        for i in range(8):
            packet.data.append(test_data[i])
            self.log.debug(f"Data length        : {len(packet.data)}")

            number = packet.convert_data_to_number()
            self.log.debug(f"All bytes, unsigned: {number}")
            # Unsigned
            self.fail_if(number != expected_values_unsigned[i],
                         f"Invalid value: {number}, expected: {expected_values_unsigned[i]}")

            # Signed
            number = packet.convert_data_to_number(signed=True)
            self.log.debug(f"All bytes, signed  : {number}")
            self.fail_if(number != expected_values_signed[i],
                         f"Invalid value: {number}, expected: {expected_values_signed[i]}")

        # Test some partial data
        number = packet.convert_data_to_number(3, 2)
        self.log.debug(f"Bytes 2, 3, 4, unsigned: {number}")
        self.fail_if(number != 2264451,
                     f"Invalid value: {number}, expected: {2264451}")
        number = packet.convert_data_to_number(3, 2, signed=True)
        self.log.debug(f"Bytes 2, 3, 4, signed  : {number}")
        self.fail_if(number != -14512765,
                     f"Invalid value: {number}, expected: {-14512765}")
        # Too many bytes
        packet.data.append(31)
        try:
            packet.convert_data_to_number()
            self.fail("No error message when data size is too big")
        except Exception as e:
            self.fail_if(str(e) != "Amount of bytes too big (> 8): 9",
                         f"Wrong error message received")

    def test_string_conversion(self):
        packet = DataPacket()
        packet.dsn = 1
        packet.ssn = 0
        packet.pid = 1
        packet.data = [76, 105, 108, 121, 84, 114, 111, 110, 105, 99, 115, 31, 127]
        data_string = packet.convert_data_to_string()
        self.log.debug(f"String: {data_string}")
        self.fail_if(data_string[-2:] != "..", "Invalid string")
        data_string = packet.convert_data_to_string(False)
        self.log.debug(f"String: {data_string}")
        self.fail_if(list(map(lambda c: ord(c), data_string[-2:])) != [31, 127], "Invalid string")


if __name__ == "__main__":

    TestDataPacket().run()
