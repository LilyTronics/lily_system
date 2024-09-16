"""
Lists all the available serial ports on the system.
"""

import threading
import time
import serial

from serial.tools.list_ports import comports

SKIP_PORTS = ["Bluetooth link"]


def get_available_serial_ports():
    ports = []
    threads = []
    lock = threading.RLock()

    serial_ports = comports()

    for port in serial_ports:
        for query in SKIP_PORTS:
            if query in port.description:
                break
        else:
            t = threading.Thread(target=_check_serial_port, args=(lock, port.device, ports))
            t.daemon = True
            t.start()
            threads.append(t)

    while True in list(map(lambda x: x.is_alive(), threads)):
        time.sleep(0.01)

    return sorted(ports)


def _check_serial_port(lock_object, port_name, port_list):
    try:
        p = serial.Serial(port_name)
        p.close()
        lock_object.acquire()
        try:
            port_list.append(port_name)
        finally:
            lock_object.release()
    except (Exception, ):
        pass


if __name__ == "__main__":

    start = time.perf_counter()
    print(get_available_serial_ports())
    stop = time.perf_counter()
    print(f"Ports detected in: {(stop - start):.3f} seconds")
