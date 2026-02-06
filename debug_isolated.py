import os

# Set cache paths BEFORE importing heavy libs
os.environ['HF_HOME'] = r'C:\Users\hayth\Desktop\SFR\Sentinel\cache\huggingface'
os.environ['SENTENCE_TRANSFORMERS_HOME'] = r'C:\Users\hayth\Desktop\SFR\Sentinel\cache\sentence_transformers'

import chromadb
from chromadb.utils import embedding_functions

print("Initializing Chroma with local persistence...")
# Use a local file path for chroma to avoid temp dir issues
client = chromadb.PersistentClient(path=r"C:\Users\hayth\Desktop\SFR\Sentinel\cache\chroma_db")

print("Initializing Embedding Function...")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

print("Creating collection...")
collection = client.get_or_create_collection(name="test_iso", embedding_function=ef)
collection.add(documents=["test"], ids=["1"])
print("Success!")
