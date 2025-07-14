from dataclasses import dataclass

from ..configs import EMGConfig


@EMGConfig.register_subclass("myo")
@dataclass
class MyoEMGConfig(EMGConfig):
    tty: str | None = None
    mac: str | None = None
    position: str | None = None

    def __post_init__(self):
        if self.tty is None:
            raise ValueError("`tty` must be provided for Myo EMG configuration.")
        if self.mac is None:
            raise ValueError("`mac` must be provided for Myo EMG configuration.")
        if self.position is None:
            raise ValueError("`position` must be provided for Myo EMG configuration.")
