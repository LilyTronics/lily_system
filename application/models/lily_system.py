"""
Lily System module.
- Detects racks/modules
- Communicates with the modules
"""

import copy
import threading
import time


class LilySystem:

    _racks = {}

    def __init__(self, event_handler):
        self._event_handler = event_handler
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()

    def __del__(self):
        if self._thread.is_alive():
            self._stop_event.set()
            self._thread.join()

    def _run(self):
        self._racks["Rack [COM3]"] = [
            {
                "id": "047C-0001",
                "slot": 3,
                "name": "Lily System signal generator"
            },
            {
                "id": "047C-0001",
                "slot": 1,
                "name": "Lily System Controller module"
            }
        ]
        self._racks["Rack [COM1]"] = [
            {
                "id": "047C-0001",
                "slot": 5,
                "name": "Lily System analyzer"
            },
            {
                "id": "047C-0001",
                "slot": 1,
                "name": "Lily System Controller module"
            }
        ]
        self._event_handler(copy.deepcopy(self._racks))
        while not self._stop_event.is_set():
            time.sleep(0.1)


if __name__ == "__main__":

    lily_system = LilySystem(print)
    time.sleep(1)
