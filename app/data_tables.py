import pandas as pd
import plotly.graph_objs as go

def load_experimental_data(non_catalyst_path, catalyst_path):
    """
    Load and create table figures for experimental data.

    Args:
        non_catalyst_path (str): Path to non-catalyst CSV file.
        catalyst_path (str): Path to catalyst CSV file.

    Returns:
        tuple: Plotly table figures for non-catalyst and catalyst data.
    """
    df_non = pd.read_csv(non_catalyst_path)
    df_cat = pd.read_csv(catalyst_path)

    non_fig = go.Figure(data=[go.Table(
        header=dict(values=list(df_non.columns), fill_color='paleturquoise', align='left'),
        cells=dict(values=[df_non[col] for col in df_non.columns], fill_color='lavender', align='left')
    )])

    cat_fig = go.Figure(data=[go.Table(
        header=dict(values=list(df_cat.columns), fill_color='paleturquoise', align='left'),
        cells=dict(values=[df_cat[col] for col in df_cat.columns], fill_color='lavender', align='left')
    )])

    return non_fig, cat_fig