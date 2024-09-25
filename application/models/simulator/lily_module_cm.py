"""
LS-CM Communication module.
"""

from application.models.simulator.lily_module import LilyModule


class LilyModuleCM(LilyModule):

    def __init__(self, slot_number, serial):
        super().__init__(slot_number, [0x04, 0x7C, 0x00, 0x01], "LS-CM Communication Module", serial, "1.0")


if __name__ == "__main__":

    from unit_tests.models.test_lily_module_cm import TestLilyModuleCm

    TestLilyModuleCm().run(True)
