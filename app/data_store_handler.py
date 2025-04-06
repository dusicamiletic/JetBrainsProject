import logging
from typing import Dict, List 
from config import PATHS 
import pandas as pd

# Configure logging
logger = logging.basicConfig(
    level=logging.INFO,
    format = '%(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class DataStoreHandler:
    
    def __init__(self):
        self.pmid_to_geo = PATHS['PMID_TO_GEO_FILE']
        
    def save_pmid_to_geo_file(self, results: Dict[str, List[str]]) -> None:
     
        try:
            with open(self.pmid_to_geo, "w") as file:
                for pmid, gse_ids in results.items():
                    file.write(f"PMID: {pmid} -> GEO IDs: {', '.join(gse_ids)}\n")
            logger.info(f"Results saved to {self.pmid_to_geo}")
            
        except Exception as e:
            logger.error(f"Error saving results to file: {str(e)}")
            raise 
            
    def save_geo_data(self, df: pd.DataFrame, output_file: str) -> None:
        """
        Save detailed GEO data from DataFrame to a text file.
        
        Args:
            df (pd.DataFrame): DataFrame containing the GEO data
            output_file (str): Path to save detailed GEO information
        """
        try:
            if df.empty:
                logger.warning("No data to save - DataFrame is empty")
                return
                
            with open(output_file, 'w', encoding='utf-8') as outfile:
                # Group by PMID to organize the output
                for pmid, group in df.groupby('PMID'):
                    outfile.write(f"PMID: {pmid}\n")
                    
                    for _, row in group.iterrows():
                        outfile.write(f"\tGEO ID: {row['GEO ID']}\n")
                        outfile.write(f"\t\tTitle: {row['Title']}\n")
                        outfile.write(f"\t\tExperiment type: {row['Experiment type']}\n")
                        outfile.write(f"\t\tSummary: {row['Summary']}\n")
                        outfile.write(f"\t\tOrganism: {row['Organism']}\n")
                        outfile.write(f"\t\tOverall design: {row['Overall design']}\n")
                    outfile.write("\n")  # Add empty line between different PMIDs
                    
            logger.info(f"Detailed GEO data stored in {output_file}")
        except Exception as e:
            logger.error(f"Error saving GEO data to file: {str(e)}")
            raise
    
            
