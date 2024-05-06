import pandas as pd
import os

DATA_INPUT_PATH = os.path.join("data", "US_Accidents_March23_sampled_500k.csv")
DATA_OUTPUT_PATH = os.path.join("data", "US_Accidents_sampled_110k.csv")
SAMPLE_SIZE = 110_000
SEED = 42

df = pd.read_csv(DATA_INPUT_PATH, header=0)
df_sampled = df.sample(n=SAMPLE_SIZE, random_state=SEED)
df_sampled.to_csv(DATA_OUTPUT_PATH, index=False)