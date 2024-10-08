"""
Send and receive data through the RS-485 serial interface.

Using a RS485 two wire interface (FTDI).
Data to be send is put in a queue.
Data being received send to a callback function.

Data cannot be sent and received simultaneously.
This is handled by the transmit and receive thread (tr_thread).
When data is being received, this is handled first.
If no data is being received, data is sent from the TX queue (if any)
"""

import queue
import serial
import threading
import time

from application.models.data_packet import DataPacket
from application.models.tcp_client import TCPClient


class RS485Driver:

    BAUD_RATE = 250000
    LOOP_DELAY_US = 300
    RX_DELAY_US = 20

    def __init__(self, serial_port, rx_callback):
        self._tx_queue = queue.Queue()
        self._rx_callback = rx_callback
        if serial_port.startswith("socket://"):
            host, port = serial_port[9:].split(":")
            self._serial = TCPClient(host, int(port))
        else:
            self._serial = serial.Serial(serial_port, self.BAUD_RATE)
        self._stop_event = threading.Event()
        self._stop_event.clear()
        self._tr_thread = threading.Thread(target=self._transmit_receive)
        self._tr_thread.daemon = True
        self._tr_thread.start()

    @staticmethod
    def _usleep(value):
        start = time.perf_counter()
        value = value / 1000000
        while (time.perf_counter() - start) < value:
            pass

    def _transmit_receive(self):
        rx_data = b""
        while not self._stop_event.is_set():
            if self._serial.in_waiting > 0:
                while self._serial.in_waiting > 0:
                    rx_data += self._serial.read(self._serial.in_waiting)
                    while True:
                        stx_pos = rx_data.find(DataPacket.STX)
                        if stx_pos >= 0:
                            rx_data = rx_data[stx_pos:]
                        else:
                            break
                        etx_pos = rx_data.find(DataPacket.ETX)
                        if etx_pos > 0:
                            self._rx_callback(rx_data[:etx_pos + 1])
                            rx_data = rx_data[etx_pos + 1:]
                        else:
                            break
                    self._usleep(self.RX_DELAY_US)
            else:
                # No bytes waiting, sending data if any
                try:
                    self._serial.write(self._tx_queue.get_nowait())
                except queue.Empty:
                    pass

            self._usleep(self.LOOP_DELAY_US)

    def get_port(self):
        return self._serial.port

    def send_data(self, data):
        self._tx_queue.put(data)

    def close(self):
        if self._tr_thread.is_alive():
            self._stop_event.set()
            self._tr_thread.join()
        self._serial.close()


if __name__ == "__main__":

    from unit_tests.models.test_rs485_driver import TestRS485Driver

    TestRS485Driver().run()
