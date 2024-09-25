"""
Data packet class.
Convert packet to send into data top send and convert received data into a packet.

Data packet format: <STX><DSN><SSN><PID><DATA><CRC><ETX>
Number of bytes   :   1    1    1    2     n    1    1
Data 1 ... 35 bytes.
Minimum packet size: 8
Maximum packet size: 42
Bytes stuffing using DLE.
"""

import struct

from application.models.crc8 import calculate_crc


class DataPacket:

    STX = 0x02
    ETX = 0x04
    DLE = 0x20
    MIN_PACKET_SIZE = 8

    # Upper case is unsigned, lower case is signed
    _BYTES_TO_FORMAT = {1: "B", 2: "H", 4: "I", 8: "Q"}

    # We use the original IBM character encoding
    _ENCODING = "cp437"

    def __init__(self):
        self.dsn = 0
        self.ssn = 0
        self.pid = 0
        self.data = []

    def __str__(self):
        output = "Properties:\n"
        output += f"DSN  : {self.dsn}\n"
        output += f"SSN  : {self.ssn}\n"
        output += f"PID  : {self.pid}\n"
        output += f"Data : {self._represent(self.data)}"
        return output

    def _init_packet(self):
        self.dsn = 0
        self.ssn = 0
        self.pid = 0
        self.data = []

    def _represent(self, data):
        output = ""
        for byte in data:
            output += f"0x{byte:02X} "
        output += f"- {self.convert_data_to_string()}"
        return output

    def _apply_byte_stuffing(self, data):
        stuffed_data = []
        for byte in data:
            if byte in [self.STX, self.ETX, self.DLE]:
                stuffed_data.append(self.DLE)
                stuffed_data.append(~byte & 0xFF)
            else:
                stuffed_data.append(byte)
        return stuffed_data

    def _remove_byte_stuffing(self, data):
        unstuffed_data = []
        stuffed_byte = False
        for byte in data:
            if byte == self.DLE:
                stuffed_byte = True
                continue
            if stuffed_byte:
                unstuffed_data.append(~byte & 0xFF)
                stuffed_byte = False
            else:
                unstuffed_data.append(byte)
        return unstuffed_data

    def from_data(self, data_bytes):
        self._init_packet()
        if len(data_bytes) >= self.MIN_PACKET_SIZE and data_bytes[0] == self.STX and data_bytes[-1] == self.ETX:
            data_bytes = self._remove_byte_stuffing(data_bytes[1:-1])
            if calculate_crc(data_bytes[:-1]) == data_bytes[-1]:
                self.dsn = data_bytes[0]
                self.ssn = data_bytes[1]
                self.pid = data_bytes[2] * 256 + data_bytes[3]
                self.data = data_bytes[4:-1]

    def get_data(self):
        data_bytes = []
        if (1 <= self.dsn <= 255 and 0 <= self.ssn <= 255 and self.dsn != self.ssn and
                1 <= self.pid <= 65535 and 1 <= len(self.data) <= 35):
            data_bytes.extend([
                self.dsn,
                self.ssn,
                (self.pid >> 8) & 0xFF,
                self.pid & 0xFF,
            ])
            data_bytes.extend(self.data)
            crc = calculate_crc(data_bytes)
            data_bytes.append(crc)
            data_bytes = self._apply_byte_stuffing(data_bytes)
            data_bytes.insert(0, self.STX)
            data_bytes.append(self.ETX)
        return bytes(data_bytes)

    def convert_data_to_number(self, n_bytes=0, offset=0, signed=False):
        if n_bytes == 0 or n_bytes > len(self.data):
            data_bytes = self.data[offset:]
        else:
            data_bytes = self.data[offset:offset + n_bytes]
        if len(data_bytes) > 8:
            raise Exception(f"Amount of bytes too big (> 8): {len(data_bytes)}")
        while len(data_bytes) not in [1, 2, 4, 8]:
            if signed:
                data_bytes.insert(0, 255)
            else:
                data_bytes.insert(0, 0)
        frmt = self._BYTES_TO_FORMAT[len(data_bytes)]
        if signed:
            frmt = frmt.lower()
        return struct.unpack(">" + frmt, bytes(data_bytes))[0]

    def convert_data_to_string(self, ascii_only=True):
        data = self.data.copy()
        if ascii_only:
            for i in range(len(data)):
                data[i] = data[i] if 31 < data[i] < 127 else 46
        return bytes(data).decode(self._ENCODING)


if __name__ == "__main__":

    from unit_tests.models.test_data_packet import TestDataPacket

    TestDataPacket().run(True)
