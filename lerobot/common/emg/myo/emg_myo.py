import threading
import queue
from ..emg import EMG
import sys

sys.path.insert(0, "/Users/jasonchan/Code/lerobot")
from pyomyo.src.pyomyo.pyomyo import Myo, emg_mode
from .configuration_myo import MyoEMGConfig
from ..configs import EMGConfig
import time

MODE = emg_mode.RAW


class EMGMyo(EMG):
    """EMG device class for Myo armband."""

    def __init__(self, config):

        super().__init__(config)

        self.myo = None

        self.mac = list(map(int, config.mac.split(":")))
        self.tty = config.tty
        self.position = config.position
        self.curr_values = None  # type: tuple[int, ...] | None

    def connection_worker(self):
        """Connect to the Myo armband.
        This method is meant to run in a separate thread to continously read EMG data.
        """
        print("MAC", self.mac, flush=True)
        m = Myo(mode=MODE, tty=self.tty)
        self.myo = m
        m.connect(input_address=self.mac)
        print("conn status in connection worker:", m.conn, flush=True)

        def add_to_queue(emg, movement):
            # curr_time = (time.time(),)
            # emg = emg + curr_time
            self.curr_values = emg

        m.add_emg_handler(add_to_queue)

        # Orange logo and bar LEDs
        m.set_leds([128, 128, 0], [128, 128, 0])
        # Vibrate to know we connected okay
        m.vibrate(1)

        """worker function"""
        while True:
            m.run()
        print("Worker Stopped")

    def connect(self):
        p = threading.Thread(target=self.connection_worker, daemon=True)
        p.start()

    def is_connected(self):
        """Check if the Myo armband is connected."""
        print(
            "RESULT OF IS CONNECTED:",
            self.myo is not None and self.myo.connected,
        )
        return self.myo is not None and self.myo.connected

    def read(self):
        """Read the past 200/30 frames of EMG data."""
        return (
            self.curr_values
            if self.curr_values is not None
            else (0, 0, 0, 0, 0, 0, 0, 0, time.time())
        )  # this is problematic because time.time() is not the same as the time in the worker thread, but it is a placeholder to avoid errors.

    def __del__(self):
        print("Disconnecting")
        self.myo.disconnect()
        print("Disconnected")

    def disconnect(self):
        """Disconnect the Myo armband."""
        print("Disconnecting Myo EMG device...")
        # self.myo.disconnect()
        print("Myo EMG device disconnected.")
