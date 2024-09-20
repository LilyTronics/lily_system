"""
Run the simulators
"""

from models.simulator.lily_module_cm import LilyModuleCM
from models.simulator.lily_simulator import LilySimulator


class Simulators:

    PORTS = [17001, 17002]

    _simulators = []

    @classmethod
    def run(cls):
        serial = 100001
        for port in cls.PORTS:
            modules = [LilyModuleCM(1, f"{serial}")]
            serial += 1
            cls._simulators.append(
                LilySimulator(port, modules)
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

    def _rx_callback(data):
        p = DataPacket()
        p.from_data(data)
        print(p)


    Simulators.run()
    print("Running:", Simulators.is_running())

    print("Connecting to the simulator")

    ports = []
    for _port in Simulators.PORTS:
        ports.append(RS485Driver(f"socket://localhost:{_port}", _rx_callback))

    # Ask the module ID for all modules
    packet = DataPacket()
    packet.dsn = 0xFF
    packet.ssn = 0
    packet.data = [3]
    print("Send data")
    for _port in ports:
        packet.pid += 1
        _port.send_data(packet.get_data())

    time.sleep(2)

    for _port in ports:
        _port.close()
