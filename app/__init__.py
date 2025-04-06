from flask import Flask
import os
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, FLASK_CONFIG

#Create Flask app with templates and data folders
template_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))
data_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'))
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

app = Flask(__name__, template_folder=template_dir)

app.config['SECRET_KEY'] = FLASK_CONFIG['SECRET_KEY']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

from app import routes 
