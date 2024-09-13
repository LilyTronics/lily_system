"""
Lily System module.
- Detects racks/modules
- Communicates with the modules
"""

import threading


class LilySystem:

    racks = []

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
        while not self._stop_event.is_set():
            pass


if __name__ == "__main__":

    lily_system = LilySystem(print)

    input("Press enter to stop")
