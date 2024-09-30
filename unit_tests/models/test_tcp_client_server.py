"""
Test the TCP client/server.
"""

import lily_unit_test
import time

from application.models.simulator.tcp_server import TCPServer
from application.models.tcp_client import TCPClient


class TestTCPClientServer(lily_unit_test.TestSuite):

    _HOST = "localhost"
    _PORT = 17120
    _TEST_DATA = b"Lily System TCP server test"

    _tcp_server = None

    @staticmethod
    def _packet_handler(data):
        # Loopback
        return [data]

    def setup(self):
        self._tcp_server = TCPServer(self._HOST, self._PORT, self._packet_handler)

    def test_loop_back(self):
        c = TCPClient(self._HOST, self._PORT)
        c.write(self._TEST_DATA)
        t = 1
        rx_data = b""
        while t > 0:
            while c.in_waiting > 0:
                rx_data += c.read(c.in_waiting)
            if rx_data == self._TEST_DATA:
                break
            time.sleep(0.1)
            t -= 0.1
        c.close()
        self.log.debug(f"RX data: {rx_data}")
        self.fail_if(rx_data != self._TEST_DATA, f"Invalid data received, expected: {self._TEST_DATA}")


if __name__ == "__main__":

    TestTCPClientServer().run()
