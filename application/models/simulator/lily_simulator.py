"""
Simulates a rack with various modules.
"""

import socket
import threading


class LilySimulator:

    _HOST = "localhost"
    _RX_BUFFER_SIZE = 1500
    _RX_TIME_OUT = 1

    def __init__(self, port):
        self._port = port
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._handle_messages)
        self._thread.daemon = True
        self._thread.start()

    def __del__(self):
        if self._thread.is_alive():
            self._stop_event.set()
            self._thread.join()

    def _handle_messages(self):
        sock = socket.create_server((self._HOST, self._port))
        sock.settimeout(self._RX_TIME_OUT)
        while not self._stop_event.is_set():
            try:
                connection = sock.accept()[0]
            except TimeoutError:
                continue
            response = self._parsing_data(connection.recv(self._RX_BUFFER_SIZE))
            if response != b"":
                connection.sendall(response)
        sock.close()

    def _parsing_data(self, data):
        response = b""
        # Start of packet
        if data[0] != 2:
            return response
        # End of packet
        if data.find(4) == -1:
            return response
        # Trim data
        data = data[1:data.find(4)]
        # We must have at least 5 bytes (dsn, ssn, pid_high, pid_low, cmd, crc)
        if len(data) < 6:
            return response
        # Check CRC
        if not self._check_crc(data):
            return response
        # Get all parts of the data
        dsn = data[0]
        ssn = data[1]
        pid = data[2] * 256 + data[3]
        cmd = data[4]
        print(dsn, ssn, pid, cmd)
        return response

    def _check_crc(self, data):
        crc = 0
        return data[-1] == crc


if __name__ == "__main__":

    import serial
    import time

    sim = LilySimulator(17000)

    s = serial.serial_for_url("socket://localhost:17000")
    s.write(b"\x02\x01\x00\x00\x01\x01\x00\x04")
    rsp = b""
    t = 2
    while t > 0:
        while s.in_waiting > 0:
            rsp += s.read(s.in_waiting)
        time.sleep(0.1)
        t -= 0.1
    print(rsp)
    s.close()
