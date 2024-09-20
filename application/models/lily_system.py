"""
Lily System module.
- Detects racks/modules
- Communicates with the modules
"""

import copy
import threading
import time

from models.data_packet import DataPacket
from models.rs485_driver import RS485Driver
from models.simulator.simulators import Simulators


class LilySystem:

    _racks = []
    _module_detect_interval = 5     # seconds
    _loop_interval = 0.1            # seconds

    # {
    #     "port": "COM3",
    #     "modules": [
    #         {
    #             "id": "047C-0002",
    #             "slot": 3,
    #             "name": "Lily System signal generator"
    #         },
    #         {
    #             "id": "047C-0001",
    #             "slot": 1,
    #             "name": "Lily System Controller module"
    #         }
    #     ]
    # }

    def __init__(self, event_handler):
        self._event_handler = event_handler
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()
        self._packet_id = 1
        self._send_packets = []

    def __del__(self):
        if self._thread.is_alive():
            self._stop_event.set()
            self._thread.join()

    def _handle_rx_packet(self, data):
        packet = DataPacket()
        packet.from_data(data)
        for port, send_packet in self._send_packets:
            if packet.pid == send_packet.pid:
                self._event_handler("Response from " + port)

    def _send_module_detection(self, port):
        # We need the ID and the name
        packet = DataPacket()
        packet.dsn = 0xFF
        packet.ssn = 0
        packet.data = [1]
        packet.pid = self._packet_id
        port.send_data(packet.get_data())
        self._send_packets.append((port.get_port(), copy.deepcopy(packet)))
        self._packet_id += 1

    def _run(self):
        open_ports = []
        if Simulators.is_running():
            try:
                open_ports.append(RS485Driver("socket://localhost:17000", self._handle_rx_packet))
                open_ports.append(RS485Driver("socket://localhost:17001", self._handle_rx_packet))
            except (Exception, ):
                pass
        t_detect = 5
        while not self._stop_event.is_set():
            # Module detection
            if t_detect >= self._module_detect_interval:
                for port in open_ports:
                    self._send_module_detection(port)
                t_detect = 0

            time.sleep(self._loop_interval)
            t_detect += self._loop_interval

    def get_racks(self):
        with self._lock:
            racks = copy.deepcopy(self._racks)
        return racks


if __name__ == "__main__":

    Simulators.run()

    lily_system = LilySystem(print)
    time.sleep(7)
