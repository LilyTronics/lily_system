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
    _module_detect_interval = 5
    _loop_interval = 0.1
    _packet_timeout = 5

    _packet_id_ranges = (
        # Normal packets (63k)
        (0x0001, 0xFBFF),
        # Module detection (1k)
        (0xFC00, 0xFFFF)
    )
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

    def __init__(self, rack_update_event):
        self._rack_update_event = rack_update_event
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._detection_thread = threading.Thread(target=self._module_detection)
        self._detection_thread.daemon = True
        self._detection_thread.start()
        self._packet_id = self._packet_id_ranges[0][0]
        self._packet_detection_id = self._packet_id_ranges[1][0]
        self._send_packets = []

    def __del__(self):
        if self._detection_thread.is_alive():
            self._stop_event.set()
            self._detection_thread.join()

    def _handle_rx_packet(self, data):
        packet = DataPacket()
        packet.from_data(data)
        with self._lock:
            for port, send_packet, timestamp in self._send_packets:
                if packet.pid == send_packet.pid:
                    # Check if the packet is from a detection
                    self._rack_update_event(port)

    def _send_module_detection(self, port):
        # We need the ID and the name
        packet = DataPacket()
        packet.dsn = 0xFF
        packet.ssn = 0
        packet.data = [1]
        packet.pid = self._packet_detection_id
        port.send_data(packet.get_data())
        with self._lock:
            self._send_packets.append((port.get_port(), copy.deepcopy(packet), time.time()))
        self._packet_detection_id += 1
        if self._packet_detection_id > self._packet_id_ranges[1][1]:
            self._packet_detection_id = self._packet_id_ranges[1][0]

    def _module_detection(self):
        open_ports = []
        if Simulators.is_running():
            try:
                for port in Simulators.PORTS:
                    open_ports.append(RS485Driver(f"socket://localhost:{port}", self._handle_rx_packet))
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

    def _rack_update(racks):
        print("Rack update:")
        print(racks)

    Simulators.run()

    lily_system = LilySystem(_rack_update)
    time.sleep(7)
