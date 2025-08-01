import abc
from dataclasses import dataclass

import draccus


@dataclass(kw_only=True)
class EMGConfig(draccus.ChoiceRegistry, abc.ABC):
    sampling_rate: int | None = None
    channels: int | None = None
    position: str | None = None
    window_length: int = 100

    @property
    def type(self) -> str:
        return self.get_choice_name(self.__class__)
