# Configure paths for Google Sheets credentials
import os

# Get the absolute path to the credentials file
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
GOOGLE_CREDS_PATH = os.path.join(BASE_DIR, "thematic-nature-455407-t7-099111c466df.json")
GOOGLE_SHEET_NAME = "Algo Trading"  # Name of your Google Sheet
