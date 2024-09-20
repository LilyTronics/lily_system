"""
Run the simulators
"""

from models.simulator.lily_module_cm import LilyModuleCM
from models.simulator.lily_simulator import LilySimulator


class Simulators:

    _simulators = []

    @classmethod
    def run(cls):
        cls._simulators.append(
            LilySimulator(17000, [
                LilyModuleCM(1, "100001")
            ])
        )
        cls._simulators.append(
            LilySimulator(17001, [
                LilyModuleCM(1, "100002")
            ])
        )

    @classmethod
    def is_running(cls):
        running = False
        if len(cls._simulators) > 0:
            running = False not in list(map(lambda s: s.is_running(), cls._simulators))
        return running


if __name__ == "__main__":

    import time

    from models.data_packet import DataPacket
    from models.rs485_driver import RS485Driver

    Simulators.run()
    print("Running:", Simulators.is_running())

    print("Connecting to the simulator")
    ports = [
        RS485Driver("socket://localhost:17000", print),
        RS485Driver("socket://localhost:17001", print)
    ]

    # Ask the module ID for all modules
    packet = DataPacket()
    packet.dsn = 0xFF
    packet.ssn = 0
    packet.pid = 1
    packet.data = [1]
    print("Send data")
    for port in ports:
        port.send_data(packet.get_data())

    time.sleep(2)

    for port in ports:
        port.close()
