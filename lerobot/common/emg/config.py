import abc
from dataclasses import dataclass

import draccus


@dataclass()
class EMGConfig(draccus.ChoiceRegistry, abc.ABC):
    sampling_rate: int | None = None
    channels: int | None = None

    @property
    def type(self) -> str:
        return self.get_choice_name(self.__class__)
