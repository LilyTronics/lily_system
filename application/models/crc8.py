"""
Calculate CRC (8 bit) over a byte array.
"""

CRC_POLY = 0x07


def calculate_crc(data_bytes):
    crc = 0
    for byte in data_bytes:
        crc ^= byte
        for _i in range(8):
            if (crc & 0x80) > 0:
                crc <<= 1
                crc ^= CRC_POLY
            else:
                crc <<= 1
            crc &= 0xFF
    return crc


if __name__ == "__main__":

    data = b""
    for i in range(10):
        data += i.to_bytes(1)
    print(f"Data: {data}")
    print(f"CRC : 0x{calculate_crc(data):X}")
