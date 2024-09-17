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

    BAUD_RATE = 1000000

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

    def _transmit_receive(self):
        rx_state = 0
        rx_data = b""
        while not self._stop_event.is_set():
            # Check for incoming bytes
            if self._serial.in_waiting == 0:
                # No bytes waiting, sending data if any
                try:
                    tx_data = self._tx_queue.get_nowait()
                    self._serial.write(tx_data)
                except queue.Empty:
                    pass
            else:
                while self._serial.in_waiting > 0:
                    data_byte = self._serial.read(1)
                    if rx_state == 0 and ord(data_byte) == DataPacket.STX:
                        rx_state += 1
                        rx_data = b""
                    elif rx_state == 1:
                        if ord(data_byte) == DataPacket.ETX:
                            self._rx_callback(rx_data)
                            rx_state = 0
                        elif ord(data_byte) == DataPacket.STX:
                            # Something went wrong
                            rx_state = 0
                        else:
                            rx_data += data_byte
                    else:
                        rx_state = 0

    def send_data(self, data):
        self._tx_queue.put(data)

    def close(self):
        if self._tr_thread.is_alive():
            self._stop_event.set()
            self._tr_thread.join()
        self._serial.close()


if __name__ == "__main__":

    _serial_port = "COM4"
    packet = DataPacket()
    packet.dsn = 1
    packet.ssn = 0
    packet.pid = 0x0305
    packet.command = 5

    rs485 = RS485Driver(_serial_port, print)

    for i in range(4):
        packet.command += 1
        rs485.send_data(packet.get_data())

    time.sleep(2)

    rs485.close()
