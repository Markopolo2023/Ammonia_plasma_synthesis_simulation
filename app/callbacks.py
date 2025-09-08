import numpy as np
from scipy.integrate import solve_ivp
from dash import Output, Input
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from app.data_processing import load_and_clean_data
from app.kinetics import saha_electron_density, get_rate_coefficient, plasma_kinetics
from app.data_export import export_simulation_data
from app.data_tables import load_experimental_data
import os

def register_callbacks(app, config):
    @app.callback(
        [Output("species-plot", "figure"), Output("sensitivity-heatmap", "figure"),
         Output("download-data", "data")],
        [Input("te-slider", "value"), Input("ratio-slider", "value"), Input("power-slider", "value"),
         Input("tg-slider", "value"), Input("export-btn", "n_clicks")]
    )
    def update_dashboard(T_e, ratio, power_density, T_g, n_clicks):
        df = load_and_clean_data(os.path.join("data", config['Data']['SimulationDataPath']))
        n_e = saha_electron_density(T_e, power_density)

        # Initial conditions: N2:H2 ratio converted to concentrations
        total_density = config.getfloat('Simulation', 'TotalDensity')
        N2_0 = total_density * (1 / (1 + 3 * ratio))
        H2_0 = total_density * (3 * ratio / (1 + 3 * ratio))
        y0 = [1e10, 1e10, H2_0, 0, 0, 0, N2_0]  # [N, H, H2, NH, NH2, NH3, N2]

        t_span = (0, config.getfloat('Simulation', 'TimeMax'))
        t_eval = np.linspace(0, config.getfloat('Simulation', 'TimeMax'), config.getint('Simulation', 'TimePoints'))

        # Simulation (using non-catalyst kinetics)
        sol = solve_ivp(plasma_kinetics, t_span, y0, method='BDF', t_eval=t_eval, args=(df, T_e, T_g, n_e, 1.0))

        # Species evolution plot
        species_fig = make_subplots(rows=1, cols=1)
        species = ['N', 'H', 'H2', 'NH', 'NH2', 'NH3', 'N2']
        for i, name in enumerate(species):
            species_fig.add_trace(go.Scatter(x=sol.t, y=sol.y[i], name=name,
                                             line=dict(color=f'rgb({50 + 30 * i}, {100 + 20 * i}, {150 - 20 * i})')))
        species_fig.update_layout(
            title=dict(text="", x=0.5, xanchor="center"),
            xaxis_title="Time (s)",
            yaxis_title="Concentration (cm⁻³)",
            template="plotly_white",
            width=1200,
            height=800,
            margin=dict(r=300)  # Increased right margin for legend
        )

        # Sensitivity heatmap (single column for current T_e)
        reactions = [
            'N + H2(v) -> H + NH',
            'NH3 + M -> NH2 + H + M',
            'NH2 + H -> NH3',
            'N + NH2 -> NH + NH'
        ]
        sensitivities = np.zeros((len(reactions), 1))  # Single column
        for i, reaction in enumerate(reactions):
            sensitivities[i, 0] = get_rate_coefficient(reaction, df, T_e, T_g)
        heatmap_fig = go.Figure(data=go.Heatmap(
            z=sensitivities, x=[f"{T_e:.1f} eV"], y=reactions, colorscale="Viridis",
            text=[[f"{z:.2e} cm³/s" for z in row] for row in sensitivities], texttemplate="%{text}",
            zmin=0, zmax=np.max(sensitivities) if np.max(sensitivities) > 0 else 1e-9,
            colorbar=dict(title=dict(text="Rate Coefficient (cm³/s)", side="right"), len=0.7, thickness=15)
        ))
        heatmap_fig.update_layout(
            title=dict(text="", x=0.5, xanchor="center"),
            xaxis_title="Electron Temperature (eV)",
            yaxis_title="Reaction",
            template="plotly_white",
            width=600,
            height=800,
            yaxis=dict(tickfont=dict(size=10), automargin=True),  # Reduced font size
            margin=dict(l=200, r=50, t=50, b=50)  # Increased left margin
        )

        # Export data
        csv_string = export_simulation_data(sol.y.T, sol.t, species)

        return species_fig, heatmap_fig, dict(content=csv_string,
                                             filename="simulation_data.csv") if n_clicks else None