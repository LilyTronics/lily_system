"""
Test getting the generic commands.
"""

import lily_unit_test

from application.models.data_packet import DataPacket
from application.models.rs485_driver import RS485Driver
from unit_tests.lib.test_settings import TestSettings


class TestGenericCommands(lily_unit_test.TestSuite):

    rs485 = None
    rx_packet = None

    def _send_packet(self, pid, data):
        self.rx_packet = None
        packet = DataPacket()
        packet.dsn = 0x01
        packet.ssn = 0x00
        packet.pid = pid
        packet.data = [data]
        self.rs485.send_data(packet.get_data())

    def _rx_callback(self, data):
        self.rx_packet = DataPacket()
        self.rx_packet.from_data(data)

    def _packet_received(self):
        return self.rx_packet is not None

    def _check_packet(self, pid, length):
        self.fail_if(not self.wait_for(self._packet_received, True, 5, 0.1), "Did not receive a packet")
        self.fail_if(self.rx_packet.dsn != 0, f"Wrong DSN: {self.rx_packet.dsn}")
        self.fail_if(self.rx_packet.ssn != 1, f"Wrong SSN: {self.rx_packet.ssn}")
        self.fail_if(self.rx_packet.pid != pid, f"Wrong PID: {self.rx_packet.pid}")
        self.fail_if(len(self.rx_packet.data) != length, f"Wrong data size: {len(self.rx_packet.data)}")

    def setup(self):
        self.rs485 = RS485Driver(TestSettings.get_serial_port(), self._rx_callback)

    def test_get_module_id(self):
        self._send_packet(1, 1)
        self._check_packet(1, 4)
        mfg_code = self.rx_packet.convert_data_to_number(2)
        self.fail_if(mfg_code != 1148, f"Wrong manufacturer code: {mfg_code}")
        module_code = self.rx_packet.convert_data_to_number(2, 2)
        self.log.debug(f"Module ID: {mfg_code:04X}-{module_code:04X}")

    def test_get_module_name(self):
        self._send_packet(2, 2)
        self._check_packet(2, 16)
        module_name = self.rx_packet.convert_data_to_string()
        self.log.debug(f"Module name: {module_name}")
        self.fail_if(not module_name.startswith("LS-"), "Invalid module name")

    def test_get_serial(self):
        self._send_packet(3, 3)
        self._check_packet(3, 6)
        serial = self.rx_packet.convert_data_to_string()
        self.log.debug(f"Serial: {serial}")

    def test_get_version(self):
        self._send_packet(4, 4)
        self._check_packet(4, 3)
        version = self.rx_packet.convert_data_to_string()
        self.log.debug(f"Version: {version}")

    def teardown(self):
        if self.rs485 is not None:
            self.rs485.close()


if __name__ == "__main__":

    TestGenericCommands().run()
