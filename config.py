import os

# Base directory - main directory of project 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File paths are now relative to BASE_DIR
PATHS = {
    "PMID_TO_GEO_FILE": os.path.join(BASE_DIR, "data", "PMID_to_GEO_results.txt"),
    "GEO_DATA_FILE": os.path.join(BASE_DIR, "data", "PMID_to_GEO_data.txt"),
    "CSV_FILE": os.path.join(BASE_DIR, "data", "geo_data.csv"),
    "P_CSV_FILE": os.path.join(BASE_DIR, "data", "p_geo_data.csv"),
    "TFIDF_FILE": os.path.join(BASE_DIR, "data", "tfidf_matrix.csv"),
    "CACHE_DIR": os.path.join(BASE_DIR, "cache")  # Directory for cache files
}

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'txt'}

# Flask configuration
FLASK_CONFIG = {
    "HOST": "127.0.0.1",
    "PORT": 5000,
    "DEBUG": True,
    "SECRET_KEY": "mykey"  
}

