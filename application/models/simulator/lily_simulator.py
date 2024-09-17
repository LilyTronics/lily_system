"""
Simulates a rack with various modules.
"""

import socket
import threading

from models.crc8 import calculate_crc
from models.data_packet import DataPacket


class LilySimulator:

    _HOST = "localhost"
    _RX_BUFFER_SIZE = 1500
    _RX_TIME_OUT = 1

    def __init__(self, port, modules):
        self._port = port
        self._modules = modules
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._handle_packets)
        self._thread.daemon = True
        self._thread.start()

    def __del__(self):
        if self._thread.is_alive():
            self._stop_event.set()
            self._thread.join()

    def _handle_packets(self):
        sock = socket.create_server((self._HOST, self._port))
        sock.settimeout(self._RX_TIME_OUT)
        while not self._stop_event.is_set():
            try:
                connection = sock.accept()[0]
            except TimeoutError:
                continue
            data = connection.recv(self._RX_BUFFER_SIZE)
            pos_stx = data.find(DataPacket.STX)
            pos_etx = data.find(DataPacket.ETX)
            if pos_stx != -1 and (pos_etx - pos_stx) >= 7:
                data = data[pos_stx:pos_etx + 1]
                crc = calculate_crc(data[1:-2])
                if crc == data[-2]:
                    responses = self._process_packet(data)
                    for response in responses:
                        connection.sendall(response)
        sock.close()

    def _process_packet(self, data):
        # Processing packets can lead to multiple responses (e.g.: broadcast)
        responses = []
        for module in self._modules:
            response = module.process_packet(data)
            if response is not None:
                responses.append(response)
        return responses


if __name__ == "__main__":

    import time

    from models.rs485_driver import RS485Driver

    sim = LilySimulator(17000, [])

    print("Connecting to the simulator")
    rs485 = RS485Driver("socket://localhost:17000", print)

    # Ask the module ID for all modules
    packet = DataPacket()
    packet.dsn = 0xFF
    packet.ssn = 0
    packet.pid = 0x0001
    packet.command = 1
    print("Send data")
    rs485.send_data(packet.get_data())

    time.sleep(2)

    rs485.close()
