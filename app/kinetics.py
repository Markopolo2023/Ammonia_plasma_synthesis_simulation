import numpy as np
import logging

logging.basicConfig(level=logging.WARNING)

def saha_electron_density(T_e, power_density):
    """
    Calculate electron density using a simplified model based on power density.

    Args:
        T_e (float): Electron temperature in eV.
        power_density (float): Power density in W/cm^3.

    Returns:
        float: Electron density in cm^-3.
    """
    # Simplified model: electron density scales with power density
    n_e_base = 1e11  # Base electron density (cm^-3) for non-thermal plasma
    scaling_factor = power_density / 1.0  # Normalize by 1 W/cm^3
    n_e = n_e_base * scaling_factor * (T_e / 2.0) ** 1.5  # Empirical scaling
    return max(n_e, 1e10)  # Ensure minimum density for stability

def get_rate_coefficient(reaction, df, T_e, T_g, E_v=0):
    """
    Retrieve and evaluate rate coefficient for a given reaction.

    Args:
        reaction (str): Reaction string (e.g., 'N + H2(v) -> H + NH').
        df (pandas.DataFrame): DataFrame with reaction data.
        T_e (float): Electron temperature in eV.
        T_g (float): Gas temperature in K.
        E_v (float): Vibrational energy in K (default 0).

    Returns:
        float: Rate coefficient in cm^3/s or appropriate units.
    """
    try:
        # Look for exact match in Reaction column
        rate_data = df[df['Reaction'].str.strip() == reaction.strip()]
        if rate_data.empty:
            logging.warning(f"No data found for reaction: {reaction}")
            return 0.0

        rate_expr = rate_data['Rate_Constant'].iloc[0]
        # Evaluate the rate expression
        if isinstance(rate_expr, str):
            # Replace mathematical functions and variables
            rate_expr = (rate_expr.replace('exp', 'np.exp')
                                  .replace('T_g', str(T_g))
                                  .replace('E_v', str(E_v))
                                  .replace('T_e', str(T_e)))
            try:
                rate = eval(rate_expr, {"np": np, "T_g": T_g, "T_e": T_e, "E_v": E_v})
                return float(rate)
            except Exception as e:
                logging.warning(f"Error evaluating rate expression '{rate_expr}' for reaction {reaction}: {e}")
                return 0.0
        else:
            return float(rate_expr)
    except Exception as e:
        logging.warning(f"Error retrieving rate coefficient for reaction {reaction}: {e}")
        return 0.0

def plasma_kinetics(t, y, df, T_e, T_g, n_e, catalyst_factor=1.0):
    """
    Define ODE system for plasma kinetics.

    Args:
        t (float): Time in seconds.
        y (numpy.ndarray): Array of species concentrations [N, H, H2, NH, NH2, NH3, N2].
        df (pandas.DataFrame): DataFrame with reaction data.
        T_e (float): Electron temperature in eV.
        T_g (float): Gas temperature in K.
        n_e (float): Electron density in cm^-3.
        catalyst_factor (float): Scaling factor for catalyst-enhanced NH3 production (default 1.0).

    Returns:
        list: Time derivatives of species concentrations.
    """
    N, H, H2, NH, NH2, NH3, N2 = y

    # Get rate coefficients from CSV
    k1 = get_rate_coefficient('N + H2(v) -> H + NH', df, T_e, T_g) * 1e3  # Scaled for faster dynamics
    k2 = get_rate_coefficient('NH3 + M -> NH2 + H + M', df, T_e, T_g) * 1e-2  # Scaled to reduce stiffness
    k3 = get_rate_coefficient('NH2 + H -> NH3', df, T_e, T_g) * 1e3 * catalyst_factor  # Catalyst-enhanced
    k4 = get_rate_coefficient('N + NH2 -> NH + NH', df, T_e, T_g) * 1e3
    k5 = get_rate_coefficient('N + H -> NH', df, T_e, T_g) * 1e3
    k6 = get_rate_coefficient('NH + H -> NH2', df, T_e, T_g) * 1e3
    k7 = get_rate_coefficient('H + NH2 -> H2 + NH', df, T_e, T_g) * 1e3

    # Electron impact dissociation rates (e + N2 -> 2N + e, e + H2 -> 2H + e)
    k_diss_N2 = 1e-9 * np.exp(-9 / T_e)  # cm3/s, adjusted for threshold ~9 eV
    k_diss_H2 = 1e-9 * np.exp(-8 / T_e)  # cm3/s, adjusted for threshold ~8 eV

    # Reaction rates
    r1 = k1 * N * H2
    r2 = k2 * NH3
    r3 = k3 * NH2 * H
    r4 = k4 * N * NH2
    r5 = k5 * N * H
    r6 = k6 * NH * H
    r7 = k7 * H * NH2
    r_diss_N2 = k_diss_N2 * n_e * N2
    r_diss_H2 = k_diss_H2 * n_e * H2

    # ODEs for species
    dN_dt = -r1 - r4 - r5 + 2 * r_diss_N2
    dH_dt = r1 + r2 - r3 - r5 - r6 - r7 + 2 * r_diss_H2
    dH2_dt = -r1 + r7 - r_diss_H2
    dNH_dt = r1 + r4 + r7 + r5 - r6
    dNH2_dt = r2 + r6 - r3 - r4 - r7
    dNH3_dt = r3 - r2
    dN2_dt = -r_diss_N2

    return [dN_dt, dH_dt, dH2_dt, dNH_dt, dNH2_dt, dNH3_dt, dN2_dt]