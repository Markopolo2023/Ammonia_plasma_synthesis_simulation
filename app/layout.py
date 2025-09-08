from dash import dcc, html
import configparser

def create_layout(non_fig, cat_fig, config):
    return html.Div(
        className="min-h-screen bg-gray-100 font-sans",
        children=[
            html.Header(
                className="bg-teal-800 text-white p-4",
                children=[
                    html.H1(config['DEFAULT']['AppTitle'], className="text-2xl font-bold"),
                    html.P("Simulate and analyze NH3 production in a plasma reactor as an alternative to Haber-Bosch.", className="text-sm")
                ]
            ),
            dcc.Tabs([
                dcc.Tab(label="Simulation", children=[
                    html.Div(
                        className="container p-4",
                        children=[
                            # Input controls with borders and tooltips
                            html.Div(
                                className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 border border-gray-300 rounded p-4 bg-white shadow",
                                children=[
                                    html.Div([
                                        html.Label("Electron Temperature (T_e, eV)", title="Average kinetic energy of electrons in the plasma, typically 1-5 eV for non-thermal plasmas.", className="block text-sm font-bold"),
                                        dcc.Slider(id="te-slider",
                                                   min=config.getfloat('Sliders', 'TeMin'),
                                                   max=config.getfloat('Sliders', 'TeMax'),
                                                   step=config.getfloat('Sliders', 'TeStep'),
                                                   value=config.getfloat('Sliders', 'TeDefault'),
                                                   marks={i: {'label': str(i), 'style': {'fontSize': '14px'}} for i in range(int(config.getfloat('Sliders', 'TeMin')), int(config.getfloat('Sliders', 'TeMax')) + 1)},
                                                   className="py-4")
                                    ]),
                                    html.Div([
                                        html.Label("Gas Flow Rate (N2:H2 ratio)", title="Ratio of nitrogen to hydrogen in the feed gas. Stoichiometric ratio is 1:3 for NH3 synthesis.", className="block text-sm font-bold"),
                                        dcc.Slider(id="ratio-slider",
                                                   min=config.getfloat('Sliders', 'RatioMin'),
                                                   max=config.getfloat('Sliders', 'RatioMax'),
                                                   step=config.getfloat('Sliders', 'RatioStep'),
                                                   value=config.getfloat('Sliders', 'RatioDefault'),
                                                   marks={0.1: {'label': "1:9", 'style': {'fontSize': '14px'}}, 0.33: {'label': "1:3", 'style': {'fontSize': '14px'}}, 0.5: {'label': "1:2", 'style': {'fontSize': '14px'}}, 1: {'label': "1:1", 'style': {'fontSize': '14px'}}},
                                                   className="py-4")
                                    ]),
                                    html.Div([
                                        html.Label("Power Density (W/cm³)", title="Deposited power per unit volume in the plasma, affecting electron density and reaction rates.", className="block text-sm font-bold"),
                                        dcc.Slider(id="power-slider",
                                                   min=config.getfloat('Sliders', 'PowerMin'),
                                                   max=config.getfloat('Sliders', 'PowerMax'),
                                                   step=config.getfloat('Sliders', 'PowerStep'),
                                                   value=config.getfloat('Sliders', 'PowerDefault'),
                                                   marks={i: {'label': str(i), 'style': {'fontSize': '14px'}} for i in range(0, int(config.getfloat('Sliders', 'PowerMax')) + 1, 2)},
                                                   className="py-4")
                                    ]),
                                    html.Div([
                                        html.Label("Gas Temperature (T_g, K)", title="Temperature of heavy species (atoms, molecules), kept low in non-thermal plasmas to prevent thermal decomposition.", className="block text-sm font-bold"),
                                        dcc.Slider(id="tg-slider",
                                                   min=config.getfloat('Sliders', 'TgMin'),
                                                   max=config.getfloat('Sliders', 'TgMax'),
                                                   step=config.getfloat('Sliders', 'TgStep'),
                                                   value=config.getfloat('Sliders', 'TgDefault'),
                                                   marks={300: {'label': "300", 'style': {'fontSize': '14px'}}, 1000: {'label': "1000", 'style': {'fontSize': '14px'}}, 2000: {'label': "2000", 'style': {'fontSize': '14px'}}},
                                                   className="py-4")
                                    ])
                                ]
                            ),
                            # Plots with borders (side by side)
                            html.Div(
                                className="flex flex-row gap-4 border border-gray-300 rounded p-4 bg-white shadow max-w-full",
                                style={'display': 'flex', 'flexDirection': 'row', 'flexWrap': 'wrap', 'width': '100%', 'maxWidth': '3000px', 'margin': '0', 'overflow': 'visible'},
                                children=[
                                    html.Div(
                                        className="border border-gray-300 rounded",
                                        style={'width': '1000px'},
                                        children=[
                                            html.H2("Species Concentration Over Time", className="text-lg font-semibold text-center", style={'textAlign': 'center'}),
                                            dcc.Graph(id="species-plot", style={'width': '1200px', 'height': '800px'})
                                        ]
                                    ),
                                    html.Div(
                                        className="border border-gray-300 rounded",
                                        style={'width': '800px'},
                                        children=[
                                            html.H2("Rate Sensitivity at Current T_e", className="text-lg font-semibold text-center", style={'textAlign': 'center'}),
                                            dcc.Graph(id="sensitivity-heatmap", style={'width': '800px', 'height': '800px'})
                                        ]
                                    )
                                ]
                            ),
                            # Key Equations (using embedded images with labels above)
                            html.Div(
                                className="border border-gray-300 rounded pl-0 p-4 bg-white shadow mt-4",
                                style={'margin': '0'},
                                children=[
                                    html.H2("Key Equations", className="text-lg font-semibold"),
                                    html.Div([
                                        html.Div(
                                            className="border border-gray-300 rounded pl-0 p-4 bg-white shadow mt-4",
                                            style={'margin': '0'},
                                            children=[
                                                html.P("Overall Reaction:", className="text-sm font-medium"),
                                                html.Img(src="https://latex.codecogs.com/png.image?\\dpi{300}\\bg{white}\\ce{N2 + 3H2 <=> 2NH3}", style={'display': 'block', 'margin': '0', 'width': '5%'})
                                            ]
                                        ),
                                        html.Div(
                                            className="border border-gray-300 rounded pl-0 p-4 bg-white shadow mt-4",
                                            style={'margin': '0'},
                                            children=[
                                                html.P("Saha Electron Density (approximation):", className="text-sm font-medium"),
                                                html.Img(src="https://latex.codecogs.com/png.image?\\dpi{300}\\bg{white}n_e = \\left( \\frac{2 \\pi m_e k T_e}{h^2} \\right)^{3/2} \\exp\\left( -\\frac{I}{2 k T_e} \\right) \\quad (\\text{cm}^{-3})", style={'display': 'block', 'margin': '0', 'width': '10%'})
                                            ]
                                        ),
                                        html.Div(
                                            className="border border-gray-300 rounded pl-0 p-4 bg-white shadow mt-4",
                                            style={'margin': '0'},
                                            children=[
                                                html.P("Rate Equation for NH3:", className="text-sm font-medium"),
                                                html.Img(src="https://latex.codecogs.com/png.image?\\dpi{300}\\bg{white}\\frac{d[\\ce{NH3}]}{dt} = k_3 [\\ce{NH2}][\\ce{H}] - k_2 [\\ce{NH3}] \\quad (\\text{cm}^{-3} \\text{s}^{-1})", style={'display': 'block', 'margin': '0', 'width': '10%'})
                                            ]
                                        ),
                                        html.Div(
                                            className="border border-gray-300 rounded pl-0 p-4 bg-white shadow mt-4",
                                            style={'margin': '0'},
                                            children=[
                                                html.P("Vibrational Enhancement (N + H2(v) → H + NH):", className="text-sm font-medium"),
                                                html.Img(src="https://latex.codecogs.com/png.image?\\dpi{300}\\bg{white}k_1 = 4 \\times 10^{-10} \\left( \\frac{T_g}{300} \\right)^{0.5} \\exp\\left( -\\frac{16600}{T_g} + \\frac{0.3 E_v}{T_g} \\right) \\quad (\\text{cm}^3 \\text{s}^{-1})", style={'display': 'block', 'margin': '0', 'width': '10%'})
                                            ]
                                        ),
                                        html.Div(
                                            className="border border-gray-300 rounded pl-0 p-4 bg-white shadow mt-4",
                                            style={'margin': '0'},
                                            children=[
                                                html.P("Electron Impact Dissociation (N2):", className="text-sm font-medium"),
                                                html.Img(src="https://latex.codecogs.com/png.image?\\dpi{300}\\bg{white}k_{\\ce{N2}} = 10^{-9} \\exp\\left( -\\frac{9}{T_e} \\right) \\quad (\\text{cm}^3 \\text{s}^{-1})", style={'display': 'block', 'margin': '0', 'width': '10%'})
                                            ]
                                        ),
                                        html.Div(
                                            className="border border-gray-300 rounded pl-0 p-4 bg-white shadow mt-4",
                                            style={'margin': '0'},
                                            children=[
                                                html.P("Electron Impact Dissociation (H2):", className="text-sm font-medium"),
                                                html.Img(src="https://latex.codecogs.com/png.image?\\dpi{300}\\bg{white}k_{\\ce{H2}} = 10^{-9} \\exp\\left( -\\frac{8}{T_e} \\right) \\quad (\\text{cm}^3 \\text{s}^{-1})", style={'display': 'block', 'margin': '0', 'width': '10%'})
                                            ]
                                        )
                                    ])
                                ]
                            ),
                            # Export button (larger)
                            html.Button("Export Simulation Data", id="export-btn",
                                        className="mt-8 bg-teal-600 text-white px-10 py-10 rounded hover:bg-teal-700 text-lg font-medium",
                                        style={'marginTop': '32px'}),
                            dcc.Download(id="download-data")
                        ]
                    )
                ]),
                dcc.Tab(label="Experimental Data", children=[
                    html.Div(
                        className="container p-4",
                        children=[
                            html.Div(
                                className="border border-gray-300 rounded p-4 bg-white shadow mb-4",
                                children=[
                                    html.H2("Non-Catalyst Experimental Data", className="text-lg font-semibold text-center"),
                                    dcc.Graph(figure=non_fig)
                                ]
                            ),
                            html.Div(
                                className="border border-gray-300 rounded p-4 bg-white shadow",
                                children=[
                                    html.H2("Catalyst Experimental Data", className="text-lg font-semibold text-center"),
                                    dcc.Graph(figure=cat_fig)
                                ]
                            )
                        ]
                    )
                ])
            ])
        ]
    )