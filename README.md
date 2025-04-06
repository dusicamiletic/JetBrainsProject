# GEO Datasets Analysis and Visualization Tool

This application analyzes and visualizes relationships between PubMed publications (PMIDs) and their associated Gene Expression Omnibus (GEO) datasets. It processes PMIDs to find corresponding GEO datasets, analyzes their content, and provides an interactive visualization of the relationships.

## Technical Overview

The application performs the following analysis:

1. **Data Retrieval**:
   - Uses NCBI's e-utils API to fetch GEO dataset IDs associated with provided PMIDs
   - Example API call: `eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=gds&linkname=pubmed_gds&id={PMID}&retmode=xml`
   - Implements caching mechanism to store API responses:
     - Once an API call is made for a specific GEO ID, the response is stored in cache
     - Subsequent requests for the same GEO ID will use cached data instead of making new API calls
     - This significantly improves processing speed for repeated PMIDs and GEO IDs

2. **Text Analysis**:
   - Extracts and combines the following GEO dataset fields:
     - Title
     - Experiment type
     - Summary
     - Organism
     - Overall design
   - Use NLP techniques for text preprocessing to clean and standardize the input
   - Applies TF-IDF vectorization to create numerical representations of the text content

3. **Analysis and Visualization**:
   - Applies Principal Component Analysis (PCA) for dimensionality reduction
   - Performs clustering to group similar datasets
   - Creates an interactive visualization showing:
     - Clusters of related GEO datasets
     - Associations between datasets and their source PMIDs

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone or download this repository to your local machine.

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Make sure your virtual environment is activated.

2. Run the application:
   ```bash
   python run.py
   ```

3. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

4. Keep the terminal window open while using the application.

## Using the Application

1. **Input PMIDs**:
   - **Manual Entry**: Enter PMIDs directly in the provided text field
   - **File Upload**: Upload a text file containing PMIDs (one PMID per line)
   - **Send via POST request**: Use the provided test_visualize_request.py script as an example to send PMIDs through a POST request in JSON format.

2. **Processing**:
   - The application will:
     - Fetch associated GEO datasets using the e-utils API
     - Extract and analyze the relevant text fields
     - Perform TF-IDF vectorization and clustering
   - Processing time may vary depending on the number of PMIDs and associated datasets

3. **Visualization**:
   - Once processing is complete, you will be redirected to the visualization page
   - The visualization shows:
     - Clusters of related GEO datasets
     - Connections between datasets and their source PMIDs
   - Access the visualization at: `http://127.0.0.1:5000/visualize`

## Features

- Support for both manual input and file upload of PMIDs
- Automated retrieval of associated GEO datasets
- TF-IDF based text analysis of GEO dataset content
- Interactive visualization of dataset clusters and PMID associations
- User-friendly web interface
- **All data retrieved and processed during analysis is stored in the  ```data ``` folder as  ```.txt ``` and  ```.csv ``` files.**
  - This allows users to inspect exact GEO ID values, text descriptions, and the full TF-IDF vectors for each GEO dataset.

## Note

- The application must remain running in the terminal while in use
- Make sure to keep the terminal window open to maintain the server connection
- Internet connection is required for API calls to NCBI's e-utils service

## Support

If you encounter any issues or have questions, please open an issue in the repository. 
