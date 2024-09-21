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

from models.data_packet import DataPacket


class RS485Driver:

    BAUD_RATE = 250000
    LOOP_DELAY_US = 300
    RX_DELAY_US = 20

    def __init__(self, serial_port, rx_callback):
        self._tx_queue = queue.Queue()
        self._rx_callback = rx_callback
        if serial_port.startswith("socket://"):
            self._serial = serial.serial_for_url(serial_port, self.BAUD_RATE)
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

    def _rx_callback(data):
        print("RX:", " ".join(map(lambda c: f"0x{c:02X}", data)))

    _serial_port = "COM4"
    packet = DataPacket()
    packet.dsn = 1
    packet.ssn = 0
    packet.pid = 0x0305
    packet.command = 5

    rs485 = RS485Driver(_serial_port, _rx_callback)
    print("Port:", rs485.get_port())
    for i in range(2):
        packet.command += 1
        tx_data = packet.get_data()
        print("TX:", " ".join(map(lambda c: f"0x{c:02X}", tx_data)))
        rs485.send_data(tx_data)

    time.sleep(1)

    rs485.close()
