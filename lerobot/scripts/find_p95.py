import numpy as np
import pandas as pd


df = pd.read_csv("/Users/jasonchan/Code/lerobot/emg_calibration.csv").values
df = df - np.median(df, axis=0, keepdims=True)
amp_t = np.sqrt((df**2).mean(axis=1))
print(f"95th {float(np.quantile(amp_t, 0.95))}")
