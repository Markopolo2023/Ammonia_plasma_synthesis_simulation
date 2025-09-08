Plasma-Enhanced Ammonia Synthesis Simulation

Overview
This project simulates plasma-enhanced ammonia (NH₃) synthesis. It provides a Dash-based web dashboard and real world data to model the kinetics of key species (N, H, H₂, NH, NH₂, NH₃, N₂) in a non-thermal plasma reactor. One can visualize species concentrations over time, analyze reaction rate sensitivities, and display governing equations. The simulation uses data from kinetic_rates.csv and parameters from config.ini.
The dashboard features interactive controls for electron temperature, gas flow ratio, power density, and gas temperature, while the notebook offers a standalone analysis environment with editable parameters and LaTeX-rendered equations.
Developed by: Markopolo2023, with assistance from Grok (xAI)Date: September 8, 2025
Features

Interactive Dashboard:
Species Evolution Plot: Visualizes concentrations of N, H, H₂, NH, NH₂, NH₃, and N₂ over time (1000px wide, 600px tall, with legend).
Rate Sensitivity Heatmap: Displays reaction rate coefficients for key reactions at the selected electron temperature (800px wide, 600px tall, with clear labels).
Parameter Controls: Sliders for electron temperature (T_e), N2:H2 ratio, power density, and gas temperature (T_g).
Export Functionality: Download simulation data as CSV.
Key Equations: Displays governing equations as images with centered labels.


Jupyter Notebook (plasma_ammonia_synthesis.ipynb):
Simulates kinetics using scipy.integrate.solve_ivp.
Generates interactive Plotly plots for species evolution and rate sensitivity.
Displays key equations in LaTeX.
Allows parameter adjustments via code variables.



Installation

Clone the Repository:
git clone https://github.com/Markopolo2023/Ammonia_plasma_synthesis_simulation.git
cd Ammonia_plasma_synthesis_simulation


Set Up a Virtual Environment (recommended):
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\activate   # Windows


Install Dependencies:
pip install dash numpy scipy pandas plotly configparser


Verify Data Files:Ensure the data/ directory contains:

catalyst_dbd_ammonia_experimental.csv
electron_cross_sections.csv
kinetic_rates.csv
non_catalyst_dbd_ammonia_experimental.csv



Usage
Running the Dashboard

Activate the virtual environment:
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\activate   # Windows


Run the Dash app:
python app.py


Open the dashboard in a browser (typically at http://127.0.0.1:8050):

Adjust sliders for T_e, N2:H2 ratio, power density, and T_g.
View Species Evolution and Rate Sensitivity Heatmap.
Click "Export Simulation Data" to download results as CSV.



Running the Jupyter Notebook

Activate the virtual environment (as above).

Start Jupyter Notebook:
jupyter notebook


Open plasma_ammonia_synthesis.ipynb in the browser.

Edit simulation parameters (e.g., T_e, ratio) in the Configuration cell and run all cells to generate plots and view equations.


Project Structure



File/Directory
Description



app.py
Main script to run the Dash application.


config.ini
Configuration file for simulation parameters and data paths.


plasma_ammonia_synthesis.ipynb
Jupyter Notebook for standalone simulation and visualization.


app/__init__.py
Initializes the app module.


app/callbacks.py
Defines Dash callbacks for interactive updates.


app/data_export.py
Handles CSV export of simulation data.


app/data_processing.py
Loads and cleans data from CSV files.


app/data_tables.py
Processes experimental data for plots.


app/kinetics.py
Implements kinetic modeling (electron density, rate coefficients, ODEs).


app/layout.py
Defines the Dash dashboard layout.


app/utils.py
Utility functions (currently empty).


data/
Directory containing CSV files with reaction and experimental data.


Dependencies

Python 3.9+
dash>=2.0
numpy>=1.20
scipy>=1.7
pandas>=1.3
plotly>=5.0
configparser>=5.0

Install via:
pip install -r requirements.txt

(Note: Create a requirements.txt with the above packages if desired.)
Configuration
Edit config.ini to customize simulation parameters:
[DEFAULT]
AppTitle = Plasma-Enhanced Ammonia Synthesis Dashboard
DebugMode = True

[Data]
SimulationDataPath = kinetic_rates.csv
NonCatalystDataPath = non_catalyst_dbd_ammonia_experimental.csv
CatalystDataPath = catalyst_dbd_ammonia_experimental.csv

[Sliders]
TeMin = 1.0
TeMax = 20.0
TeStep = 0.1
TeDefault = 2.0
RatioMin = 0.1
RatioMax = 1.0
RatioStep = 0.01
RatioDefault = 0.33
PowerMin = 0.0
PowerMax = 20.0
PowerStep = 0.1
PowerDefault = 1.0
TgMin = 300.0
TgMax = 1000.0
TgStep = 10.0
TgDefault = 300.0

[Simulation]
TotalDensity = 2.5e19
TimeMax = 1000.0
TimePoints = 100

Key Equations
The simulation is governed by the following equations:

Overall Reaction:$$ \ce{N2 + 3H2 <=> 2NH3} $$

Saha Electron Density (approximation):$$ n_e = \left( \frac{2 \pi m_e k T_e}{h^2} \right)^{3/2} \exp\left( -\frac{I}{2 k T_e} \right) \quad (\text{cm}^{-3}) $$

Rate Equation for NH3:$$ \frac{d[\ce{NH3}]}{dt} = k_3 [\ce{NH2}][\ce{H}] - k_2 [\ce{NH3}] \quad (\text{cm}^{-3} \text{s}^{-1}) $$

Vibrational Enhancement (N + H2(v) → H + NH):$$ k_1 = 4 \times 10^{-10} \left( \frac{T_g}{300} \right)^{0.5} \exp\left( -\frac{16600}{T_g} + \frac{0.3 E_v}{T_g} \right) \quad (\text{cm}^3 \text{s}^{-1}) $$

Electron Impact Dissociation (N2):$$ k_{\ce{N2}} = 10^{-9} \exp\left( -\frac{9}{T_e} \right) \quad (\text{cm}^3 \text{s}^{-1}) $$

Electron Impact Dissociation (H2):$$ k_{\ce{H2}} = 10^{-9} \exp\left( -\frac{8}{T_e} \right) \quad (\text{cm}^3 \text{s}^{-1}) $$


Limitations

The kinetic model is simplified and does not fully represent real plasma systems.
Experimental data visualization (from catalyst_dbd_ammonia_experimental.csv and non_catalyst_dbd_ammonia_experimental.csv) is only in the dashboard’s Experimental Data tab, not the notebook.
The dashboard requires a web browser; the notebook is standalone but less interactive.

Contributing
Contributions are welcome! Please:

Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Commit changes (git commit -am 'Add your feature').
Push to the branch (git push origin feature/your-feature).
Create a pull request.

Report issues or suggest features on the GitHub Issues page.
License
This project is licensed under the MIT License. See the LICENSE file for details.
