import threading
import queue

import numpy as np
from ..emg import EMG
import sys

sys.path.insert(0, "/Users/jasonchan/Code/lerobot")
from pyomyo.src.pyomyo.pyomyo import Myo, emg_mode
from .configuration_myo import MyoEMGConfig
from ..configs import EMGConfig
import time

MODE = emg_mode.PREPROCESSED


class ContextCacher:
    """Cache the end of input data and prepend the next input data with it.

    Args:
        window_length (int): how big the sliding window is. built-in stride of chunk's shape at dim 0.
        important note: the way its used right now, stride MUST be 1 to be interpreted correctly.
    """

    def __init__(self, window_length: int):
        self.window_length = window_length
        self.curr_window = np.zeros(
            (window_length, 8), dtype=np.float32
        )  # for 8 channels of EMG data

    def __call__(self, chunk: np.array):
        self.curr_window = np.concatenate((self.curr_window[chunk.shape[0] :], chunk))
        assert chunk.shape[0] == 1
        assert self.curr_window.shape[0] == self.window_length
        return self.curr_window


class EMGMyo(EMG):
    """EMG device class for Myo armband."""

    def __init__(self, config):

        super().__init__(config)

        self.myo = None

        self.mac = list(map(int, config.mac.split(":")))
        self.tty = config.tty
        self.position = config.position
        self.window_length = config.window_length
        self.cacher = ContextCacher(self.window_length)
        self.curr_values = None

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
            self.curr_values = self.cacher(
                np.expand_dims(np.array(emg, dtype=np.float32), axis=0)
            )

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
        """Read a single EMG data frame."""
        return self.curr_values

    def __del__(self):
        print("Disconnecting")
        self.myo.disconnect()
        print("Disconnected")

    def disconnect(self):
        """Disconnect the Myo armband."""
        print("Disconnecting Myo EMG device...")
        # self.myo.disconnect()
        print("Myo EMG device disconnected.")
