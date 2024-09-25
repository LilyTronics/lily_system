"""
Test for the simulator module LS-CM.
"""

import lily_unit_test

from application.models.data_packet import DataPacket
from application.models.simulator.lily_module_cm import LilyModuleCM


class TestLilyModuleCm(lily_unit_test.TestSuite):

    _module = None
    _slot_number = 1
    _module_id = [0x04, 0x7C, 0x00, 0x01]
    _name = "LS-CM Communication Module"
    _serial = "1A2B3C"
    _version = "1.0"

    def _send_packet(self, pid, data, slot_number=_slot_number, check_response=True):
        packet = DataPacket()
        packet.dsn = slot_number
        packet.ssn = 0
        packet.pid = pid
        packet.data = data
        response = self._module.process_packet(packet.get_data())
        if check_response:
            self.fail_if(response is None, "No response packet from module")
            self.fail_if(response.dsn != 0, f"Wrong DSN: {packet.dsn}, expected: 0")
            self.fail_if(response.ssn != self._slot_number, f"Wrong SSN: {packet.ssn}, expected: {self._slot_number}")
            self.fail_if(response.pid != pid, f"Wrong PID: {packet.pid}, expected: {pid}")
            self.fail_if(len(response.data) == 0, "No data in response packet")
            return response.data

        return response

    def setup(self):
        self._module = LilyModuleCM(self._slot_number, self._serial)

    def test_get_module_id(self):
        data = self._send_packet(1, [1])
        self.log.debug(f"Module ID: {data}")
        self.fail_if(data != self._module_id, f"Wrong module ID: {data}, expected: {self._module_id}")

    def test_get_module_name(self):
        data = self._send_packet(2, [2])
        data = "".join([chr(d) for d in data])
        self.log.debug(f"Name: {data}")
        self.fail_if(data != self._name, f"Wrong name: {data}, expected: {self._name}")

    def test_get_module_serial(self):
        data = self._send_packet(3, [3])
        data = "".join([chr(d) for d in data])
        self.log.debug(f"Serial: {data}")
        self.fail_if(data != self._serial, f"Wrong serial: {data}, expected: {self._serial}")

    def test_get_module_version(self):
        data = self._send_packet(4, [4])
        data = "".join([chr(d) for d in data])
        self.log.debug(f"Version: {data}")
        self.fail_if(data != self._version, f"Wrong version: {data}, expected: {self._version}")

    def test_invalid_slot_number(self):
        response = self._send_packet(5, [1], 2, False)
        self.fail_if(response is not None, "Received a response when there should be no response")

    def test_invalid_commands(self):
        for i in range(5, 256):
            response = self._send_packet(5, [i], 2, False)
            self.fail_if(response is not None,
                         f"Received a response for command: {i}, when there should be no response")


if __name__ == "__main__":

    TestLilyModuleCm().run(True)
