"""
Base class for a module.
"""

from application.models.data_packet import DataPacket


class LilyModule:

    def __init__(self, slot_number, module_id, name, serial, version):
        self._slot_number = slot_number
        self._module_id = module_id
        self._name = name
        self._serial = serial
        self._version = version

    def _process_generic_commands(self, data):
        output = []
        if data[0] == 1:
            # Module ID
            output = self._module_id
        elif data[0] == 2:
            # Name
            output = [ord(c) for c in self._name]
        elif data[0] == 3:
            # Serial
            output = [ord(c) for c in self._serial]
        elif data[0] == 4:
            # Version
            output = [ord(c) for c in self._version]
        return output

    def process_packet(self, data):
        response = None
        packet = DataPacket()
        packet.from_data(data)
        if packet.dsn == 255 or packet.dsn == self._slot_number and len(packet.data) > 0:
            if 0 < packet.data[0] <= 0x32:
                packet.data = self._process_generic_commands(packet.data)
            if len(packet.data) > 0:
                response = packet
                packet.dsn = packet.ssn
                packet.ssn = self._slot_number
        return response


if __name__ == "__main__":

    module = LilyModule(1, b"\x04\x7C\x00\x01", "LS-CM Communication Module", "1A2B3C", "1.0")

    print("Get module ID")
    test_packet = DataPacket()
    test_packet.dsn = 0xFF
    test_packet.ssn = 0
    test_packet.pid = 1
    test_packet.data = [1]
    print(module.process_packet(test_packet.get_data()))

    print("\nGet name")
    test_packet.dsn = 1
    test_packet.pid = 2
    test_packet.data = [2]
    print(module.process_packet(test_packet.get_data()))

    print("\nGet serial")
    test_packet.dsn = 1
    test_packet.pid = 3
    test_packet.data = [3]
    print(module.process_packet(test_packet.get_data()))

    print("\nGet version")
    test_packet.dsn = 1
    test_packet.pid = 4
    test_packet.data = [4]
    print(module.process_packet(test_packet.get_data()))

    print("\nGet name from invalid slot")
    test_packet.dsn = 10
    test_packet.pid = 5
    test_packet.data = [1]
    print(module.process_packet(test_packet.get_data()))
