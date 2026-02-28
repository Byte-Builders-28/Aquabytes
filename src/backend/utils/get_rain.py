import pandas as pd

# Load the dataset
df = pd.read_csv("ml/datasets/rainfall.csv")

# Filter only the "Mean" row
mean_row_df = df[df.iloc[:, 2] == "Mean"]  # assuming the 3rd column (index 2) has "Mean"/"Standard d"/"Coefficient"

# Column 16 is index 15
col_index = 14

# Make dictionary {region: value}
mean_values = mean_row_df.set_index("SUBDIVISION").iloc[:, col_index].to_dict()

def get_mean_rainfall(region: str) -> float:
    return mean_values.get(region.upper(), None)

# # Example
# region = "SOUTH IN"
# value = get_mean_column16(region)
# print(f"Mean value (col 16) for {region}: {value}")
