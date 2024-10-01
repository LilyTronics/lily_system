"""
Test RS485 driver.
"""

import copy
import lily_unit_test
import queue
import random

from application.models.data_packet import DataPacket
from application.models.rs485_driver import RS485Driver
from application.models.simulator.tcp_server import TCPServer


class TestRS485Driver(lily_unit_test.TestSuite):

    _HOST = "localhost"
    _PORT = 17120

    _tcp_server = None
    _rs485_driver = None
    _rx_queue = queue.Queue()

    @staticmethod
    def _tcp_callback(data):
        # loopback
        packet = DataPacket()
        packet.from_data(data)
        packet.ssn = 2
        packet.dsn = 1
        packet.data = [2]
        return [packet.get_data()]

    def _rs485_callback(self, data):
        packet = DataPacket()
        packet.from_data(data)
        self._rx_queue.put(packet)

    def setup(self):
        self._tcp_server = TCPServer(self._HOST, self._PORT, self._tcp_callback)
        self._rs485_driver = RS485Driver(f"socket://{self._HOST}:{self._PORT}", self._rs485_callback)

    def test_loop_back(self):
        packet = DataPacket()
        packet.dsn = 2
        packet.ssn = 1
        packet.pid = 1
        packet.data = [1]
        self._rs485_driver.send_data(packet.get_data())
        try:
            packet = self._rx_queue.get(True, 1)
        except queue.Empty:
            self.fail("No packet received")
        self.fail_if(packet.dsn != 1, f"Invalid DSN, received {packet.dsn}, expected 1")
        self.fail_if(packet.ssn != 2, f"Invalid SSN, received {packet.ssn}, expected 2")
        self.fail_if(packet.pid != 1, f"Invalid PID, received {packet.pid}, expected 1")
        self.fail_if(packet.data != [2], f"Invalid data, received {packet.data}, expected [2]")

    def test_random_packets(self):
        tx_packets = []
        # Generate a bunch of packets
        packet = DataPacket()
        packet.dsn = 2
        packet.ssn = 1
        packet.data = [1]
        for i in range(50):
            packet.pid = 1 + i
            tx_packets.append(copy.copy(packet))
        self.log.debug("Sending packets at random interval")
        for packet in tx_packets:
            self.sleep(random.uniform(0.05, 0.4))
            self._rs485_driver.send_data(packet.get_data())

        self.log.debug("Check for received packets")
        rx_packets = []
        while len(rx_packets) < len(tx_packets):
            try:
                rx_packets.append(self._rx_queue.get(True, 1))
            except queue.Empty:
                self.fail("Not all packets received")

        self.log.debug("Analyse received packets")
        # Check if every send packet has a response
        for tx_packet in tx_packets:
            matches = list(filter(lambda x: x.pid == tx_packet.pid, rx_packets))
            self.fail_if(len(matches) == 0, f"Packet with PID: {tx_packet.pid} has no response")


if __name__ == "__main__":

    TestRS485Driver().run()
