"""
Base class for a module.
"""

from application.models.data_packet import DataPacket


class LilyModule:

    _COMMAND_TO_DATA = {
        1: "_module_id",
        2: "_name",
        3: "_serial",
        4: "_version"
    }

    def __init__(self, slot_number, module_id, name, serial, version):
        self._slot_number = slot_number
        self._module_id = module_id
        self._name = name
        self._serial = serial
        self._version = version

    def _process_generic_commands(self, data):
        output = []
        attribute_name = self._COMMAND_TO_DATA.get(data[0], None)
        if attribute_name is None:
            return output
        attribute = getattr(self, attribute_name)
        if isinstance(attribute, str):
            attribute = [ord(c) for c in attribute]
        output = attribute
        return output

    def process_packet(self, data):
        response = None
        packet = DataPacket()
        packet.from_data(data)
        if len(packet.data) > 0 and packet.dsn == 255 or packet.dsn == self._slot_number:
            if 0 < packet.data[0] <= 0x32:
                packet.data = self._process_generic_commands(packet.data)
            if len(packet.data) > 0:
                response = packet
                packet.dsn = packet.ssn
                packet.ssn = self._slot_number
        return response


if __name__ == "__main__":

    from unit_tests.models.test_lily_module_cm import TestLilyModuleCm

    TestLilyModuleCm().run(True)
