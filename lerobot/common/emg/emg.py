import abc
from typing import Any, Dict, List
import numpy as np


class EMG(abc.ABC):

    def __init__(self, config: Dict[str, Any]):
        """Initialize the EMG device with the given configuration.

        Args:
            config: Configuration dictionary containing device settings.
        """
        self.sampling_rate = config.get("sampling_rate", 200)
        self.channels = config.get("channels", 8)
        self.position = config.get("position", "unknown")
        self.connected = False

    @property
    @abc.abstractmethod
    def is_connected(self) -> bool:
        """Check if the EMG device is currently connected.

        Returns:
            bool: True if the EMG device is connected, False otherwise.
        """
        pass

    @abc.abstractmethod
    def connect(self) -> None:
        """Establish connection to the EMG device.

        This method should handle any necessary setup or initialization
        required to start capturing EMG data.
        """
        pass

    @abc.abstractmethod
    def read(self) -> np.ndarray:
        """Capture and return a single EMG data frame at a single time point

        Returns:
            np.ndarray: Captured EMG data as a numpy array.
        """
        pass
