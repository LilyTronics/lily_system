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

from models.crc8 import calculate_crc


class DataPacket:

    STX = 0x02
    ETX = 0x04
    DLE = 0x20
    MIN_PACKET_SIZE = 8

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
        output += f"Data : {self._represent(self.data)}\n"
        output += f"Bytes: {self.get_data()}"
        return output

    def _init_packet(self):
        self.dsn = 0
        self.ssn = 0
        self.pid = 0
        self.data = []

    @staticmethod
    def _represent(data):
        hex_output = []
        ascii_output = ""
        for byte in data:
            hex_output.append(f"0x{byte:02X}")
            if 31 < byte < 127:
                ascii_output += chr(byte)
            else:
                ascii_output += "."
        return f"{" ".join(hex_output)} - {ascii_output}"

    def _apply_byte_stuffing(self, data):
        stuffed_data = []
        for byte in data:
            if byte in [ self.STX, self.ETX, self.DLE]:
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

    def from_data(self, data):
        self._init_packet()
        if data[0] == self.STX and data[-1] == self.ETX and len(data) >= self.MIN_PACKET_SIZE:
            data = self._remove_byte_stuffing(data[1:-1])
            if calculate_crc(data[:-1]) == data[-1]:
                self.dsn = data[0]
                self.ssn = data[1]
                self.pid = data[2] * 256 + data[3]
                self.data = data[4:-1]

    def get_data(self):
        data = [
            self.dsn,
            self.ssn,
            (self.pid >> 8) & 0xFF,
            self.pid & 0xFF,
        ]
        data.extend(self.data)
        crc = calculate_crc(data)
        data.append(crc)
        data = self._apply_byte_stuffing(data)
        data.insert(0, self.STX)
        data.append(self.ETX)
        return bytes(data)


if __name__ == "__main__":

    packet = DataPacket()
    packet.dsn = 1
    packet.ssn = 3
    packet.pid = 0x0506
    packet.data = [0x07, 0x11, 0x20]
    print(packet)

    packet.from_data(b"\x02\x01\x03\x05\x06\x07\x11 \xdf\x89\x04")
    print(packet)
