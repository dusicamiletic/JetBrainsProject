import logging
import pandas as pd
import plotly.express as px
from app.data_processor import DataProcessor
from config import PATHS


logger = logging.getLogger(__name__)

class DataVisualizer:
    """Handles the visualization of GEO dataset clusters."""
    
    def __init__(self):
        self.data_processor = DataProcessor()
        self.latest_graph = None
        

    def visualize(self, df):
        """Generate a 3D visualization of GEO dataset clusters."""
        try:
            # Preprocess data and save 
            p_df = self.data_processor.preprocess_dataFrame(df)
            p_df.to_csv(PATHS["P_CSV_FILE"], index=False)
            logger.info(f"Saved preprocessed DataFrame to {PATHS['P_CSV_FILE']}")
            
            # Create TF-IDF vectors and save
            X_tfidf, tfidf_df = self.data_processor.tf_idf_vectorizer(p_df)
            tfidf_df.to_csv(PATHS["TFIDF_FILE"], index=False)
            logger.info(f"Saved TF-IDF matrix to {PATHS['TFIDF_FILE']}")
            
            # Perform PCA
            X_pca = self.data_processor.compute_pca(X_tfidf)
            df_pca = pd.DataFrame(X_pca, columns=["PC1", "PC2", "PC3"])
            
            # Perform clustering
            kmeans, cluster_labels = self.data_processor.compute_clusters(X_tfidf, 3)
            p_df['Cluster'] = cluster_labels
            df_pca["Cluster"] = p_df["Cluster"]  
            df_pca["Cluster_Label"] = "Cluster " + df_pca["Cluster"].astype(str)
            df_pca["GEO ID"] = p_df["GEO ID"]
            df_pca["PMID"] = p_df["PMID"]
        
            # Create visualization
            fig = px.scatter_3d(
                df_pca,
                x="PC1", y="PC2", z="PC3",
                color="Cluster_Label",
                hover_data={"PC1": False, "PC2": False, "PC3":False, "GEO ID": True, "PMID": True},
                title="GEO Dataset Clusters Based on TF-IDF Analysis",
                labels={
                    "PC1": "Principal Component 1",
                    "PC2": "Principal Component 2",
                    "PC3":"Principal Component 3"
                }
            )  
            fig.update_traces(marker=dict(size=10))
            fig.update_layout(
                legend_title_text="Cluster", 
                height=800,
                margin=dict(l=0, r=0, t=30, b=0)
            )
        
            # Convert to HTML
            self.latest_graph = fig.to_html(
                full_html=False,
                include_plotlyjs=True,
                default_width='100%',
                default_height='100%'
            ).encode('utf-8').decode('utf-8')
            logger.info("Visualization generated successfully")
            
            return self.latest_graph

        except Exception as e:
            logger.error(f"Error during visualization: {str(e)}")
            raise


