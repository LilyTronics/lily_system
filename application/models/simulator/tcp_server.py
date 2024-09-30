"""
TCP server used in the simulator but also in the unit tests.
"""

import socket
import threading


class TCPServer:

    _BUFFER_SIZE = 1500
    _RX_TIME_OUT = 1

    def __init__(self, host, port, packet_handler):
        self._host = host
        self._port = port
        self._packet_handler = packet_handler
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._tcp_server)
        self._thread.daemon = True
        self._thread.start()

    def _tcp_server(self):
        # Create a socket for receiving and transmitting packages
        with socket.create_server((self._host, self._port)) as sock:
            while not self._stop_event.is_set():
                try:
                    connection = sock.accept()[0]
                except TimeoutError:
                    continue
                data = connection.recv(self._BUFFER_SIZE)
                for response in self._packet_handler(data):
                    connection.sendall(response)


if __name__ == "__main__":

    from unit_tests.models.test_tcp_client_server import TestTCPServer

    TestTCPServer().run()
