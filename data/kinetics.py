import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def saha_electron_density(T_e, I=15.58, n_a=1e16):
    """
    Calculate electron density using the Saha equation.

    Args:
        T_e (float): Electron temperature in eV.
        I (float): Ionization energy in eV (default: 15.58 for N2).
        n_a (float): Neutral atom density in cm^-3 (default: 1e16).

    Returns:
        float: Electron density in cm^-3.
    """
    k = 8.617e-5  # Boltzmann constant in eV/K
    m_e = 9.109e-31  # Electron mass in kg
    h = 6.626e-34  # Planck constant in J·s
    T_k = T_e / k  # Convert eV to K
    return (2 * (2 * np.pi * m_e * k * T_k / h ** 2) ** (3 / 2)) * np.exp(-I / T_e) * n_a


def get_rate_coefficient(reaction, df, T_e=2.0, T_g=300):
    """
    Get the rate coefficient for a reaction, evaluating expressions if needed.

    Args:
        reaction (str): The reaction string (e.g., 'N + H2 → NH + H').
        df (pandas.DataFrame): DataFrame containing reaction data.
        T_e (float): Electron temperature in eV.
        T_g (float): Gas temperature in K.

    Returns:
        float: Rate coefficient value (cm³/s) or 0 if not found/evaluation fails.
    """
    row = df[df['Reaction'] == reaction]
    if row.empty:
        logging.warning(f"No data found for reaction: {reaction}")
        return 0
    value = row['Value'].iloc[0]
    if isinstance(value, str) and ('Te' in value or 'Tg' in value):
        try:
            rate = eval(value.replace('^', '**'), {'Te': T_e, 'Tg': T_g, 'exp': np.exp})
            logging.debug(f"Rate for {reaction}: {rate}")
            return rate
        except Exception as e:
            logging.error(f"Failed to evaluate rate for {reaction}: {value}, error: {e}")
            return 0
    try:
        rate = float(value)
        logging.debug(f"Rate for {reaction}: {rate}")
        return rate
    except ValueError:
        logging.warning(f"Cannot convert value to float for {reaction}: {value}")
        return 0


def plasma_kinetics(y, t, df, T_e, T_g, n_e):
    """
    ODE system for plasma kinetics, tracking species evolution.

    Args:
        y (list): Current concentrations [N, H2, NH, NH2, NH3, N2].
        t (float): Time in seconds.
        df (pandas.DataFrame): DataFrame with reaction data.
        T_e (float): Electron temperature in eV.
        T_g (float): Gas temperature in K.
        n_e (float): Electron density in cm^-3.

    Returns:
        list: Derivatives [dN/dt, dH2/dt, dNH/dt, dNH2/dt, dNH3/dt, dN2/dt].
    """
    N, H2, NH, NH2, NH3, N2 = y
    rates = {
        'N + H2 → NH + H': get_rate_coefficient('N + H2 → NH + H', df, T_e, T_g),
        'e + NH3 → NH2 + H': get_rate_coefficient('e + NH3 → NH2 + H', df, T_e),
        'H + NH2 → NH3 + H': get_rate_coefficient('H2 + NH2 → NH3 + H', df, T_g),  # Note: Check if 'H2' should be 'H'
        'NH + NH2 → NH3 + N': get_rate_coefficient('NH + NH2 → NH3 + N', df, T_g),
        # Additional NH3-producing reaction from CSV
        'e + NH3 → NH + H2': get_rate_coefficient('e + NH3 → NH + H2', df, T_e)
    }

    dN_dt = -rates['N + H2 → NH + H'] * N * H2 + rates['NH + NH2 → NH3 + N'] * N * NH2
    dH2_dt = -rates['N + H2 → NH + H'] * N * H2 + rates['H + NH2 → NH3 + H'] * NH2 + rates[
        'e + NH3 → NH + H2'] * n_e * NH3
    dNH_dt = rates['N + H2 → NH + H'] * N * H2 - rates['NH + NH2 → NH3 + N'] * N * NH2 + rates[
        'e + NH3 → NH + H2'] * n_e * NH3
    dNH2_dt = rates['e + NH3 → NH2 + H'] * n_e * NH3 - rates['H + NH2 → NH3 + H'] * NH2 - rates[
        'NH + NH2 → NH3 + N'] * N * NH2
    dNH3_dt = rates['H + NH2 → NH3 + H'] * NH2 + rates['NH + NH2 → NH3 + N'] * N * NH2 - rates[
        'e + NH3 → NH2 + H'] * n_e * NH3 - rates['e + NH3 → NH + H2'] * n_e * NH3
    dN2_dt = 0  # Simplified, assuming N2 is abundant

    return [dN_dt, dH2_dt, dNH_dt, dNH2_dt, dNH3_dt, dN2_dt]