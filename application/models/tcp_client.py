"""
TCP client for connecting to the simulator.
Must have same methods as the serial port class.
"""

import socket
import threading


class TCPClient:

    _BUFFER_SIZE = 1500

    def __init__(self, host, port):
        self.in_waiting = 0
        self._rx_data = b""
        self._lock = threading.RLock()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((host, port))
        self._rx_thread = threading.Thread(target=self._handle_rx_packets)
        self._rx_thread.daemon = True
        self._rx_thread.start()

    def __del__(self):
        self.close()

    def _handle_rx_packets(self):
        while True:
            data = self._sock.recv(self._BUFFER_SIZE)
            if len(data) > 0:
                with self._lock:
                    self._rx_data += data
                    self.in_waiting = len(self._rx_data)

    def read(self, n_bytes=1):
        with self._lock:
            data_out = self._rx_data[:n_bytes]
            self._rx_data = self._rx_data[n_bytes:]
            self.in_waiting = len(self._rx_data)
        return data_out

    def write(self, data):
        self._sock.sendall(data)

    def close(self):
        try:
            self._sock.shutdown()
            self._sock.close()
        except (Exception,):
            pass


if __name__ == "__main__":

    from unit_tests.models.test_tcp_client_server import TestTCPClientServer

    TestTCPClientServer().run()
