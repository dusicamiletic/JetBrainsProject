import logging
from typing import Optional, Tuple
import pandas as pd 
import numpy as np 
import re 
import nltk 
from nltk.corpus import stopwords
from nltk import PorterStemmer
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from scipy.sparse import csr_matrix



#Configure logging
logging.basicConfig(
    level = logging.INFO,
    format = '%(levelname)s - %(message)s'        
)
logger = logging.getLogger(__name__)

#Download required NLTK data
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')  


class DataProcessor:
    """Processes and transforms text data using NLP techniques."""
    
    def __init__(self):
        self.data=None
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.vectorizer = TfidfVectorizer(
            max_features=50,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
   
    def preprocess_text(self, text: Optional[str]) -> str:
        """Preprocess text by cleaning, removing stopwords, and lemmatizing."""
        if text is None:
            return ""
        # Remove special characters, keep letters and numbers
        text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
        # Remove standalone numbers
        text = re.sub(r'(?<!\w)\d+(?!\w)', ' ', text)
        # Convert to lowercase
        text = text.lower()
        # Remove stopwords
        text = [word for word in text.split(' ') if word not in stopwords.words('english')]
        # Lemmatize words
        text = [self.lemmatizer.lemmatize(word) for word in text]
        # Remove empty strings
        text = [word for word in text if len(word) != 0]
    
        return " ".join(text)  
    
    
    def preprocess_dataFrame(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess text columns in the DataFrame"""
        text_columns = ['Title', 'Experiment type', 'Summary', 'Organism', 'Overall design']   
        processed_df = pd.DataFrame({
            'PMID': df['PMID'],
            'GEO ID': df['GEO ID'],
            **{col: df[col].apply(self.preprocess_text) for col in text_columns}
    
        })
        logger.info(f"Preprocessed DataFrame with {len(processed_df)} rows")
        return processed_df
    
    
    def tf_idf_vectorizer(self, df: pd.DataFrame) -> Tuple[csr_matrix, pd.DataFrame]:
        """
        Create TF-IDF vectors from text columns.
        
        Returns:
            Tuple containing:
            - Sparse matrix (csr_matrix): For PCA and other matrix operations
            - DataFrame: For easy viewing and manipulation of the TF-IDF features
        """
        text_columns = ['Title', 'Experiment type', 'Summary', 'Organism', 'Overall design']
        corpus = df[text_columns].agg(' '.join, axis=1) 
        X_tfidf = self.vectorizer.fit_transform(corpus)
        tfidf_df = pd.DataFrame(
            X_tfidf.toarray(),
            columns = self.vectorizer.get_feature_names_out()
        )
        logger.info(f"Created TF-IDF matrix with {tfidf_df.shape[1]} features")

        return X_tfidf, tfidf_df
    

    def compute_pca(self, tfidf_matrix) -> np.ndarray:
        """Perform PCA on the TF-IDF matrix."""
        pca = PCA(n_components=3)
        return pca.fit_transform(tfidf_matrix.toarray())   
    
    
    def compute_clusters(self, tfidf_matrix: np.ndarray, n_clusters: int):
        """Compute clusters using KMeans. Return both the model and lables."""
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit_predict(tfidf_matrix)
        return kmeans, kmeans.labels_

        
  