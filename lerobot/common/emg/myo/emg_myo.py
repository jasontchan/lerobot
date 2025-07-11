import multiprocessing
import queue
from ..emg import EMG
from pyomyo.src.pyomyo.pyomyo import Myo, emg_mode
import time

MODE = emg_mode.RAW


class EMGMyo(EMG):
    """EMG device class for Myo armband."""

    def __init__(self, config):

        super().__init__(config)

        self.mac = None
        self.tty = None
        self.q = queue.Queue()

    def connection_worker(self):
        """Connect to the Myo armband.
        This method is meant to run in a separate thread to continously read EMG data.
        """
        print("MAC", self.mac, flush=True)
        m = Myo(mode=MODE, tty=self.tty)
        m.connect(input_address=self.mac)

        def add_to_queue(emg, movement):
            curr_time = (time.time(),)
            emg = emg + curr_time
            self.q.put(emg)

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
        p = multiprocessing.Process(
            target=self.connection_worker,
        )
        p.start()

    def read(self):
        """Read a single EMG data frame."""
        if self.q.empty():
            return None
        return self.q.get()
