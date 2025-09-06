import numpy as np
import scipy.integrate as integrate
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from data import load_and_clean_data, saha_electron_density, get_rate_coefficient, plasma_kinetics, \
    export_simulation_data
import os

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Plasma-Enhanced Ammonia Synthesis Dashboard"

# Layout with modern industrial theme
app.layout = html.Div(
    className="min-h-screen bg-gray-100 font-sans",
    children=[
        html.Header(
            className="bg-blue-800 text-white p-4",
            children=[
                html.H1("Plasma-Enhanced Ammonia Synthesis", className="text-2xl font-bold"),
                html.P("Simulate and analyze NH3 production in a plasma reactor.", className="text-sm")
            ]
        ),
        html.Div(
            className="container mx-auto p-4",
            children=[
                # Input controls
                html.Div(
                    className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4",
                    children=[
                        html.Div([
                            html.Label("Electron Temperature (T_e, eV)", className="block text-sm font-medium"),
                            dcc.Slider(id="te-slider", min=1, max=5, step=0.1, value=2.0,
                                       marks={i: str(i) for i in range(1, 6)})
                        ]),
                        html.Div([
                            html.Label("Gas Flow Rate (N2:H2 ratio)", className="block text-sm font-medium"),
                            dcc.Slider(id="ratio-slider", min=0.1, max=1.0, step=0.1, value=0.33,
                                       marks={0.1: "1:9", 0.33: "1:3", 0.5: "1:2", 1: "1:1"})
                        ]),
                        html.Div([
                            html.Label("Power Density (W/cm³)", className="block text-sm font-medium"),
                            dcc.Slider(id="power-slider", min=0.1, max=10, step=0.1, value=1.0,
                                       marks={i: str(i) for i in range(0, 11, 2)})
                        ]),
                        html.Div([
                            html.Label("Gas Temperature (T_g, K)", className="block text-sm font-medium"),
                            dcc.Slider(id="tg-slider", min=300, max=1000, step=50, value=300,
                                       marks={300: "300", 1000: "1000"})
                        ])
                    ]
                ),
                # Plots
                html.Div(
                    className="grid grid-cols-1 md:grid-cols-2 gap-4",
                    children=[
                        html.Div([
                            html.H2("Species Evolution", className="text-lg font-semibold"),
                            dcc.Graph(id="species-plot")
                        ]),
                        html.Div([
                            html.H2("Energy Efficiency Comparison", className="text-lg font-semibold"),
                            dcc.Graph(id="efficiency-bar")
                        ])
                    ]
                ),
                html.Div([
                    html.H2("Rate Sensitivity Heatmap", className="text-lg font-semibold"),
                    dcc.Graph(id="sensitivity-heatmap")
                ]),
                # Export button
                html.Button("Export Simulation Data", id="export-btn",
                            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"),
                dcc.Download(id="download-data")
            ]
        )
    ]
)


# Energy efficiency calculation
def energy_efficiency(NH3_produced, power_density, volume=1e-3):
    """
    Calculate energy efficiency of NH3 production.

    Args:
        NH3_produced (float): NH3 concentration in cm^-3.
        power_density (float): Power density in W/cm^3.
        volume (float): Reactor volume in cm^3 (default: 1e-3).

    Returns:
        float: Energy efficiency in MJ/mol.
    """
    energy_per_mole = (power_density * 1e6 * 3600) / (NH3_produced * 6.022e23)  # J/mol
    return energy_per_mole / 1e6  # MJ/mol


# Callback for updating plots
@app.callback(
    [Output("species-plot", "figure"), Output("efficiency-bar", "figure"), Output("sensitivity-heatmap", "figure"),
     Output("download-data", "data")],
    [Input("te-slider", "value"), Input("ratio-slider", "value"), Input("power-slider", "value"),
     Input("tg-slider", "value"), Input("export-btn", "n_clicks")]
)
def update_dashboard(T_e, ratio, power_density, T_g, n_clicks):
    df = load_and_clean_data(
        os.path.join("data", "plasma_ammonia_synthesis_dbd_no_catalyst_data.csv"))  # CSV in data/ subdirectory
    n_e = saha_electron_density(T_e)

    # Initial conditions: N2:H2 ratio converted to concentrations
    total_density = 1e16  # cm^-3
    N2_0 = total_density * (1 / (1 + 3 * ratio))
    H2_0 = total_density * (3 * ratio / (1 + 3 * ratio))
    y0 = [0, H2_0, 0, 0, 0, N2_0]  # [N, H2, NH, NH2, NH3, N2]

    t = np.linspace(0, 1e-3, 100)  # Time in seconds
    sol = integrate.odeint(plasma_kinetics, y0, t, args=(df, T_e, T_g, n_e))

    # Species evolution plot
    species_fig = make_subplots(rows=1, cols=1, subplot_titles=["Species Concentration Over Time"])
    species = ['N', 'H2', 'NH', 'NH2', 'NH3', 'N2']
    for i, name in enumerate(species):
        species_fig.add_trace(go.Scatter(x=t * 1e3, y=sol[:, i], name=name,
                                         line=dict(color=f'rgb({50 + 30 * i}, {100 + 20 * i}, {150 - 20 * i})')))
    species_fig.update_layout(xaxis_title="Time (ms)", yaxis_title="Concentration (cm⁻³)", template="plotly_white")

    # Energy efficiency comparison
    NH3_produced = sol[-1, 4]
    plasma_efficiency = energy_efficiency(NH3_produced, power_density)
    haber_bosch_efficiency = 0.45  # MJ/mol, typical value
    efficiency_fig = go.Figure(data=[
        go.Bar(x=["Plasma", "Haber-Bosch"], y=[plasma_efficiency, haber_bosch_efficiency],
               marker_color=['#1f77b4', '#ff7f0e'])
    ])
    efficiency_fig.update_layout(title="Energy Efficiency Comparison", yaxis_title="MJ/mol NH3",
                                 template="plotly_white")

    # Sensitivity heatmap
    reactions = ['N + H2 → NH + H', 'e + NH3 → NH2 + H', 'H + NH2 → NH3 + H', 'NH + NH2 → NH3 + N']
    T_e_values = np.linspace(1, 5, 5)
    sensitivities = np.zeros((len(reactions), len(T_e_values)))
    for i, reaction in enumerate(reactions):
        for j, T_e_val in enumerate(T_e_values):
            sensitivities[i, j] = get_rate_coefficient(reaction, df, T_e_val, T_g)
    heatmap_fig = go.Figure(data=go.Heatmap(
        z=sensitivities, x=T_e_values, y=reactions, colorscale="Viridis",
        text=[[f"{z:.2e}" for z in row] for row in sensitivities], texttemplate="%{text}"
    ))
    heatmap_fig.update_layout(title="Rate Sensitivity to Electron Temperature", xaxis_title="T_e (eV)",
                              template="plotly_white")

    # Export data
    csv_string = export_simulation_data(sol, t, species)

    return species_fig, efficiency_fig, heatmap_fig, dict(content=csv_string,
                                                          filename="simulation_data.csv") if n_clicks else None


# Run the app
if __name__ == '__main__':
    app.run(debug=True)