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

    from unit_tests.models.test_crc8 import TestCrc8

    TestCrc8().run(True)
