"""
LS-CM Communication module.
"""

from models.simulator.lily_module import LilyModule


class LilyModuleCM(LilyModule):

    def __init__(self, slot_number, serial):
        super().__init__(slot_number, b"\x04\x7C\x00\x01", "LS-CM Communication Module", serial, "1.0")


if __name__ == "__main__":

    from models.data_packet import DataPacket

    module = LilyModuleCM(1, "1A2B3C")

    print("Get module ID")
    test_packet = DataPacket()
    test_packet.dsn = 0xFF
    test_packet.ssn = 0
    test_packet.pid = 1
    test_packet.data = [1]
    print(module.process_packet(test_packet.get_data()))
