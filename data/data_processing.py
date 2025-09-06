import pandas as pd
import numpy as np


def load_and_clean_data(filename):
    """
    Load and clean the CSV data, keeping expressions as strings.

    Args:
        filename (str): Path to the CSV file.

    Returns:
        pandas.DataFrame: Cleaned DataFrame with stripped and non-null values.
    """
    df = pd.read_csv(filename, skipinitialspace=True)
    df['Value'] = df['Value'].str.strip().replace('', np.nan)
    df = df.dropna(subset=['Value'])
    # Keep expressions as strings; evaluation happens in get_rate_coefficient
    return df