from lerobot.common.emg.emg import EMG
from lerobot.common.emg.configs import EMGConfig


def make_emg_streams_from_configs(emg_configs: dict[str, EMGConfig]) -> dict[str, EMG]:
    emg_streams = {}

    for key, cfg in emg_configs.items():
        if cfg.type == "myo":
            from .myo.emg_myo import EMGMyo

            emg_streams[key] = EMGMyo(cfg)
        else:
            raise ValueError(f"The EMG type '{cfg.type}' is not valid.")

    return emg_streams
