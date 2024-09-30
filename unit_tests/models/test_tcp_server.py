"""
Test the TCP server.
"""

import lily_unit_test
import serial
import time

from application.models.simulator.tcp_server import TCPServer


class TestTCPServer(lily_unit_test.TestSuite):

    _HOST = "localhost"
    _PORT = 17120
    _tcp_server = None

    @staticmethod
    def _packet_handler(data):
        return [data]

    def setup(self):
        self._tcp_server = TCPServer(self._HOST, self._PORT, self._packet_handler)

    def test_loop_back(self):
        s = serial.serial_for_url(f"socket://{self._HOST}:{self._PORT}")
        s.write(b"Hello world")
        t = 2
        rx_data = b""
        while t > 0:
            while s.in_waiting > 0:
                rx_data += s.read(s.in_waiting)
            print(rx_data)
            time.sleep(0.1)
            t -= 0.1
        s.close()


if __name__ == "__main__":

    TestTCPServer().run()
