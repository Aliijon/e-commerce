import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from rank_bm25 import BM25Okapi
import re
from typing import List, Dict, Any
import string
import unicodedata

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

def is_persian(text: str) -> bool:
    """Check if the text contains Persian characters."""
    persian_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    return bool(persian_pattern.search(text))

def tokenize_persian(text: str) -> List[str]:
    """Tokenize Persian text."""
    # Remove diacritics
    text = unicodedata.normalize('NFKD', text)
    # Split on whitespace and punctuation
    tokens = re.findall(r'\b\w+\b', text)
    return tokens

class SearchEngine:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        # Add Persian stop words
        self.persian_stop_words = set([
            'و', 'در', 'به', 'از', 'که', 'این', 'را', 'با', 'است', 'برای',
            'آن', 'یک', 'خود', 'تا', 'کرد', 'بر', 'هم', 'نیز', 'می', 'ما',
            'یا', 'هر', 'نه', 'مثل', 'اما', 'باید', 'دو', 'شد', 'هست', 'نیست',
            'وقتی', 'هی', 'شاید', 'چه', 'چرا', 'کنند', 'دارد', 'چون', 'اگر'
        ])
        self.stop_words.update(self.persian_stop_words)
        self.bm25 = None
        self.products = []
        self.processed_corpus = []

    def preprocess_text(self, text: str) -> str:
        """Preprocess text by handling both English and Persian text."""
        if not text:
            return ""

        # Detect if text contains Persian
        contains_persian = is_persian(text)
        
        try:
            if contains_persian:
                # Handle Persian text
                # Remove diacritics and normalize
                text = unicodedata.normalize('NFKD', text)
                # Tokenize Persian text
                tokens = tokenize_persian(text)
                # Remove Persian stop words
                tokens = [token for token in tokens if token not in self.persian_stop_words]
            else:
                # Handle English text
                # Convert to lowercase (only for English)
                text = text.lower()
                # Remove punctuation
                text = text.translate(str.maketrans("", "", string.punctuation))
                # Tokenize
                tokens = word_tokenize(text)
                # Remove stop words and apply stemming
                tokens = [self.stemmer.stem(token) for token in tokens if token not in self.stop_words]
            
            return " ".join(tokens)
        except Exception as e:
            # If any error occurs during preprocessing, return original tokens
            # This ensures the search still works even if preprocessing fails
            return " ".join(text.split())

    def update_index(self, products: List[Dict[str, Any]]) -> None:
        """Update the search index with new products."""
        self.products = products
        
        # Create corpus from product data
        corpus = []
        for product in products:
            # Combine name, description, and category for better search
            text = f"{product.name} {product.description} {product.category}"
            try:
                processed_text = self.preprocess_text(text)
                corpus.append(processed_text)
            except Exception as e:
                # If preprocessing fails, use original text
                corpus.append(text)
        
        # Update processed corpus
        self.processed_corpus = [doc.split() for doc in corpus]
        
        # Create BM25 index
        try:
            self.bm25 = BM25Okapi(self.processed_corpus)
        except Exception as e:
            # If BM25 creation fails, log error
            print(f"Error creating search index: {e}")
            self.bm25 = None

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search products using BM25 ranking with error handling."""
        if not self.bm25:
            return []

        try:
            # Preprocess query
            processed_query = self.preprocess_text(query)
            query_tokens = processed_query.split()

            # Get scores and indices
            scores = self.bm25.get_scores(query_tokens)
            
            # Create list of (score, index) tuples and sort by score
            scored_indices = list(enumerate(scores))
            scored_indices.sort(key=lambda x: x[1], reverse=True)

            # Get top results
            results = []
            for idx, score in scored_indices[:limit]:
                if score > 0:  # Only include relevant results
                    results.append(self.products[idx])

            return results
        except Exception as e:
            # If search fails, fall back to simple text matching
            query_lower = query.lower()
            results = []
            for product in self.products:
                if (query_lower in product.name.lower() or 
                    query_lower in product.description.lower() or 
                    query_lower in product.category.lower()):
                    results.append(product)
            return results[:limit]

# Initialize search engine
search_engine = SearchEngine() 