import requests
import logging
from typing import Optional, List, Dict
import xml.etree.ElementTree as ET
import re
import pandas as pd 
import json
import os
from config import PATHS


# Configure logging 
logger = logging.basicConfig(
    level = logging.INFO,
    format = '%(name)s - %(levelname)s - %(message)s'
    
)

logger = logging.getLogger(__name__)


class DataHandler():
    
    def __init__(self):
        self.file_path = None
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.link_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
        # Initialize cache file path
        self.cache_file = os.path.join(PATHS['CACHE_DIR'], 'geo_cache.json')
        # Load cache from file
        self.geo_cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """Load cache from file if it exists."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading cache: {str(e)}")
            return {}
            
    def _save_cache(self) -> None:
        """Save cache to file."""
        try:
            # Ensure cache directory exists
            os.makedirs(PATHS['CACHE_DIR'], exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.geo_cache, f)
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")
            
    def clear_cache(self) -> None:
        """Clear the cache file."""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                self.geo_cache = {}
                logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
        
    def set_file_path(self, file_path: str) -> None:
        self.file_path = file_path
        
    def get_file_path(self) -> Optional[str]:
        return self.file_path
    
    def load_pmids_from_file(self) -> List[str]:
        
        if self.file_path == None:
            error_msg = "File path not set. Use set_file_path() first."
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        try:
            with open(self.file_path, "r") as file:
                pmids = [line.strip() for line in file.readlines()]
            logger.info(f"Successfully loaded {len(pmids)} PMIDs from file.")
            return pmids
        
        except FileNotFoundError:
            error_msg = f"File not found: {self.file_path}"
            logger.error(error_msg)
            raise 
        
        except Exception as e:
            error_msg = f"Error loading PMIDs: {str(e)}"
            logger.error(error_msg)
            raise
            
    def get_geo_ids_from_pmids(self, pmids: List[str]) -> Dict[str, List[str]]:
        
        geo_ids = {}
        
        for pmid in pmids:
            
            params = {
                "dbfrom" : "pubmed",
                "db" : "gds", 
                "linkname" : "pubmed_gds",
                "id" : pmid, 
                "retmode": "xml"           
            }
            
            try:
                response = requests.get(self.link_url, params = params)
                response.raise_for_status()
                
                root = ET.fromstring(response.content)
                gse_ids = [id_elem.text for id_elem in root.findall(".//Link/Id") ]
                geo_ids[pmid] = gse_ids if gse_ids else ["No GEO IDs connected"]
                logger.info(f"{len(gse_ids)} GEO IDs retrieved for PMID: {pmid}")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for PMID {pmid}: {str(e)}")
                geo_ids[pmid]=["Request error"]
                
            except ET.ParseError as e:
                logger.error(f"XML parsing error for PMID {pmid}: {str(e)}")
                geo_ids[pmid]=["Parsing error"]
                
            except Exception as e:
                logger.error(f"Unexpected error for PMID {pmid}: {str(e)}")
                geo_ids[pmid]=["Unexpected error"]
                
        return geo_ids
    
    
    
    def get_overall_design(self, bioproject_id: str) -> str:
        """
        Get overall design information from a BioProject ID.
        
        Args:
            bioproject_id (str): BioProject ID to query
            
        Returns:
            str: Overall design description or "N/A if not found"
        """
        if bioproject_id == "N/A":
            return "N/A"
        
        try:
            params = {
                "db" : "bioproject",
                "id": bioproject_id,
                "retmode" : "xml"
            }
            logger.info(f"API call is made for bioproject id: {bioproject_id}")
            response = requests.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                params = params
            )

            response.raise_for_status()
            
            response_text = response.text
            start_tag = "<Description>"
            end_tag = "</Description>"
            
            description_start = response_text.find(start_tag)
            description_end = response_text.find(end_tag)
            
            if description_start != -1 and description_end != -1:
                description = response_text[description_start + len(start_tag): description_end].strip()
                match = re.search(r"Overall design:(.*)", description)
                return match.group(1).strip() if match else "N/A"
            
            logger.warning(f"No description found for BioProject {bioproject_id}")
            return "N/A"
        
        except Exception as e:
            logger.error(f"Error getting overall design for BioProject {bioproject_id}: {str(e)}")
            return "N/A"
        
    def get_geo_data(self, geo_id:str)-> tuple:
        
        """
        Get detailed information for a GEO dataset.
        
        Args:
            geo_id (str): GEO dataset ID
            
        Returns:
            tuple: (tittle, experiment_type, summary, organism, overall_design)
        """
        # Check cache first
        if geo_id in self.geo_cache:
            logger.info(f"Using cached data for GEO ID: {geo_id}")
            cached_data = self.geo_cache[geo_id]
            return tuple(cached_data)
            
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        
        params = {
            "db":"gds",
            "id": geo_id, 
            "retmode":"json"
        }
        
        try:
            logger.info(f"API call is made for GEO ID: {geo_id}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data=response.json() 
            if "result" not in data:
                logger.error(f"No result found for GEO ID {geo_id}")
                return "N/A", "N/A", "N/A", "N/A", "N/A"
 
            dataset = data["result"][geo_id]
            title = dataset.get("title", "N/A")
            exp_type = dataset.get("gdstype", "N/A")
            summary = dataset.get("summary", "N/A")
            organism = dataset.get("taxon", "N/A") 
            bioproject_id = dataset.get("bioproject", "N/A")  
            overall_design = self.get_overall_design(bioproject_id)
            
            # Cache the result
            result = [title, exp_type, summary, organism, overall_design]
            self.geo_cache[geo_id] = result
            self._save_cache()  # Save cache to file
            
            logger.info(f"Successfully retrieved and cached data for GEO ID {geo_id}")
            return tuple(result)
        
        except Exception as e:
            logger.error(f"Error processing GEO ID {geo_id}: {str(e)}")
            return "N/A", "N/A", "N/A", "N/A", "N/A"
           
    def process_pmid_geo_data(self, geo_ids: Dict[str, List[str]]) -> pd.DataFrame:
        """
        Process PMID to GEO mapping and create a DataFrame with all information.
        
        Args:
            geo_ids (Dict[str, List[str]]): Dictionary mapping PMIDs to their associated GEO IDs
            
        Returns:
            pd.DataFrame: DataFrame containing all GEO dataset information
        """
        records = []
        
        for pmid, gse_ids in geo_ids.items():
            for geo_id in gse_ids:
                # Skip error messages and invalid IDs
                if geo_id in ["No GEO IDs connected", "Request error", "Parse error", "Unexpected error"]:
                    continue
                    
                # Get detailed GEO data
                title, exp_type, summary, organism, overall_design = self.get_geo_data(geo_id)
                
                # Create record
                record = {
                    "PMID": pmid,
                    "GEO ID": geo_id,
                    "Title": title,
                    "Experiment type": exp_type,
                    "Summary": summary,
                    "Organism": organism,
                    "Overall design": overall_design
                }
                records.append(record)
                
        # Create DataFrame
        df = pd.DataFrame(records)
        logger.info(f"Created DataFrame with {len(df)} records")
        return df
    
    
        
               
                
                
        
        
        
