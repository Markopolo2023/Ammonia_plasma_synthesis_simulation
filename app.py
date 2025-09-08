import dash
from dash import html
import configparser
import os
import sys
from app.layout import create_layout
from app.callbacks import register_callbacks
from app.data_tables import load_experimental_data

# Debug: Print current directory and sys.path to diagnose import issues
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Read configuration
config = configparser.ConfigParser()
try:
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
except Exception as e:
    print(f"Error reading config.ini: {e}")
    sys.exit(1)

# Initialize Dash app
app = dash.Dash(__name__)
app.title = config['DEFAULT']['AppTitle']

# Load experimental data
try:
    non_fig, cat_fig = load_experimental_data(
        os.path.join('data', config['Data']['NonCatalystDataPath']),
        os.path.join('data', config['Data']['CatalystDataPath'])
    )
except Exception as e:
    print(f"Error loading experimental data: {e}")
    sys.exit(1)

# Set layout
try:
    app.layout = create_layout(non_fig, cat_fig, config)
except Exception as e:
    print(f"Error setting layout: {e}")
    sys.exit(1)

# Register callbacks
try:
    register_callbacks(app, config)
except Exception as e:
    print(f"Error registering callbacks: {e}")
    sys.exit(1)

if __name__ == '__main__':
    app.run(debug=config.getboolean('DEFAULT', 'DebugMode'))