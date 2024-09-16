"""
Run the simulators
"""

from models.simulator.lily_simulator import LilySimulator


def run_simulators():
    LilySimulator(17000)
    LilySimulator(17001)


if __name__ == "__main__":

    run_simulators()
