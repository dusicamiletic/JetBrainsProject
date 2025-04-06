import logging
from flask import request, jsonify, redirect, url_for, render_template, session 

# This works because app was already created in __init__.py
from app import app
from app.data_handler import DataHandler 
from app.data_store_handler import DataStoreHandler
from app.data_visualizer import DataVisualizer
from config import PATHS


logger = logging.basicConfig(
    level=logging.INFO,
    format = '%(name)s - %(levelname)s - %(message)'
)

logger = logging.getLogger(__name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/', methods=['GET'])
def home():
    """Render the home page with visualization."""
    session.clear()
    return render_template('pmids_form.html')     

@app.route('/process_manual', methods=['POST'])
def process_manual():
    """Load PMIDs from input form."""
    try:
        pmids = request.form['pmids']  # Take PMIDs from FORM 
        pmids_list = [pmid.strip() for pmid in pmids.split(',')]
        
        # Store PMIDs in session to pass to visualize route
        session['pmids'] = pmids_list
        logger.info(f"Stored PMIDs in session: {pmids_list}")
        
        # Redirect to visualize route
        return redirect(url_for('visualize'))
    except Exception as e:
        logger.error(f"Error in process_manual: {str(e)}")
        return jsonify({"error": str(e)}), 500
    

@app.route('/process_file', methods=['POST'])
def process_file():
    """Load PMIDs from file form."""
    try:
        
        uploaded_file = request.files.get('file')
        file_content = uploaded_file.read().decode("utf-8")
        pmids_list = [line.strip() for line in file_content.splitlines() if line.strip()]
        
        # Store PMIDs in session to pass to visualize route
        session['pmids'] = pmids_list 
        # Redirect to visualize route
        return redirect(url_for('visualize'))
    except Exception as e:
        logger.error(f"Error in process_file: {str(e)}")
        return jsonify({"error": str(e)}), 500 


@app.route('/visualize', methods=['GET'])
def visualize():
    """Process PMIDs and generate cluster visualization."""
    logger.info("Received visualization request")
    
    # Get PMIDs from previous process routes
    pmids = session.get('pmids', [])
    logger.info(f"Retrieved PMIDs from session: {pmids}")
    
    if not pmids:
        logger.warning("No PMIDs provided")
        return render_template('index.html', graph_html=None)

    try:
        # Process PMIDs and get GEO data
        data_handler = DataHandler()
        data_store_handler = DataStoreHandler()
        
        pmid_geo_dict = data_handler.get_geo_ids_from_pmids(pmids)
        logger.info(f"Retrieved GEO IDs for PMIDs: {pmid_geo_dict}")
        
        # Save PMIDs to GEO IDs in .txt file
        data_store_handler.save_pmid_to_geo_file(pmid_geo_dict)
        
        # Convert to DataFrame
        df = data_handler.process_pmid_geo_data(pmid_geo_dict)
        df.to_csv(PATHS["CSV_FILE"], index=False, encoding = 'utf-8')
        logger.info(f"Saved DataFrame to {PATHS['CSV_FILE']}")
        
        # Save detailed GEO data in .txt file
        data_store_handler.save_geo_data(df, PATHS["GEO_DATA_FILE"])
        
        # Generate visualization
        visualizer = DataVisualizer()
        graph_html = visualizer.visualize(df)
        logger.info("Generated visualization successfully")
        
        return render_template('index.html', graph_html=graph_html)

    except Exception as e:
        logger.error(f"Error during visualization: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
    
  
