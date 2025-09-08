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
    # Handle both 'Value' and 'Rate_Constant' columns for compatibility
    value_column = 'Rate_Constant' if 'Rate_Constant' in df.columns else 'Value'
    df[value_column] = df[value_column].str.strip().replace('', np.nan)
    df = df.dropna(subset=[value_column])
    # Keep expressions as strings; evaluation happens in get_rate_coefficient
    return df