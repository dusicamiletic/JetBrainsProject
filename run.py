from app import app
from config import FLASK_CONFIG

if __name__ == '__main__':
    print("Starting server at http://127.0.0.1:5000")
    print("Keep this window open while using the application")
    app.run(
        host=FLASK_CONFIG['HOST'],
        port=FLASK_CONFIG['PORT'],
        debug=FLASK_CONFIG['DEBUG']
    )
    
    
    