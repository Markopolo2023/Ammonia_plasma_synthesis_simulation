import pandas as pd


def export_simulation_data(sol, t, species):
    """
    Export simulation results to a CSV string.

    Args:
        sol (numpy.ndarray): ODE solution array with species concentrations.
        t (numpy.ndarray): Time array in seconds.
        species (list): List of species names.

    Returns:
        str: CSV string of the simulation data.
    """
    export_data = pd.DataFrame(sol, columns=species)
    export_data['Time (ms)'] = t * 1e3
    return export_data.to_csv(index=False)