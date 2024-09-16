"""
Data packet class.
Convert packet to send into data top send and convert received data into a packet.

Data packet format: <STX><DSN><SSN><PID><DATA><CRC><ETX>
Number of bytes   :   1    1    1    2    35    1    1
Data max 35 bytes.
Bytes stuffing using DLE.
"""


class DataPacket:

    STX = 0x02
    ETX = 0x04
    DLE = 0x20
    CRC_POLY = 0x07

    def __init__(self):
        self.dsn = 0
        self.ssn = 0
        self.pid = 0
        self.command = 0

    def _calculate_crc(self, data_bytes):
        crc = 0
        for byte in data_bytes:
            crc ^= byte
            for _i in range(8):
                if (crc & 0x80) > 0:
                    crc <<= 1
                    crc ^= self.CRC_POLY
                else:
                    crc <<= 1
                crc &= 0xFF
        return crc

    def _apply_byte_stuffing(self, data_bytes):
        stuffed_data = []
        for byte in data_bytes:
            if byte in [ self.STX, self.ETX, self.DLE]:
                stuffed_data.append(self.DLE)
                stuffed_data.append(~byte & 0xFF)
            else:
                stuffed_data.append(byte)
        return stuffed_data

    def get_data(self):
        data = [
            self.dsn,
            self.ssn,
            (self.pid >> 8) & 0xFF,
            self.pid & 0xFF,
            self.command
        ]
        crc = self._calculate_crc(data)
        data.append(crc)
        data = self._apply_byte_stuffing(data)
        return bytes([self.STX]) + bytes(data) + bytes([self.ETX])


if __name__ == "__main__":

    packet = DataPacket()
    packet.dsn = 4
    packet.ssn = 2
    packet.pid = 0x0103
    packet.command = 0x20

    print(packet.get_data())
