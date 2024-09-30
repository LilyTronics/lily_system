"""
Test for listing serial ports
"""

import lily_unit_test
import serial
import time

from application.models.list_serial_ports import get_available_serial_ports


class TestListSerialPorts(lily_unit_test.TestSuite):

    _ports = []

    def test_speed(self):
        start = time.perf_counter()
        self._ports = get_available_serial_ports()
        stop = time.perf_counter()
        diff = stop - start
        self.log.debug(f"Ports detected in: {diff:.2f} seconds")
        self.log.debug(f"Ports: {self._ports}")
        self.fail_if(diff > 1, "Detection tool more that 1 second")

    def test_if_port_open(self):
        if len(self._ports) < 1:
            self.log.debug("Cannot do test with less than 1 ports")
        else:
            s = serial.Serial(self._ports[0])
            ports = get_available_serial_ports()
            s.close()
            self.log.debug(f"Ports: {ports}")
            self.fail_if(len(self._ports) == len(ports), "Port was still detected while being open")
            self.fail_if(self._ports[0] in ports, "The open port is still in the list of available ports")


if __name__ == "__main__":

    TestListSerialPorts().run()
