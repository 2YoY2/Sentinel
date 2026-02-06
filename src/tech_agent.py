import os
import chromadb
from chromadb.utils import embedding_functions
import sys

# --- FIX: Set cache paths BEFORE importing heavy libs to avoid permission errors ---
CACHE_BASE = r"C:\Users\hayth\Desktop\SFR\Sentinel\cache"
os.environ['HF_HOME'] = os.path.join(CACHE_BASE, 'huggingface')
os.environ['SENTENCE_TRANSFORMERS_HOME'] = os.path.join(CACHE_BASE, 'sentence_transformers')

class TechnicalAgent:
    def __init__(self, data_dir=r"C:\Users\hayth\Desktop\SFR\Sentinel\data"):
        self.data_dir = data_dir
        self.kb_file = os.path.join(data_dir, "knowledge_base.txt")
        self.chroma_path = os.path.join(CACHE_BASE, "chroma_db")
        
        # Initialize ChromaDB with LOCAL persistence
        try:
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
            
            # Use a lightweight embedding model
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
            
            self.collection = self.chroma_client.get_or_create_collection(
                name="tech_manuals",
                embedding_function=self.embedding_fn
            )
            
            # Load data immediately
            self._load_knowledge_base()
        except Exception as e:
            print(f"Error initializing Tech Agent: {e}", file=sys.stderr)

    def _load_knowledge_base(self):
        """Reads the text file and indexes it."""
        if not os.path.exists(self.kb_file):
            print(f"Warning: Knowledge base not found at {self.kb_file}", file=sys.stderr)
            return

        with open(self.kb_file, "r", encoding="utf-8") as f:
            text = f.read()

        # Simple splitting by sections
        sections = text.split("##")
        
        documents = []
        ids = []
        metadatas = []

        for i, section in enumerate(sections):
            content = section.strip()
            if not content: continue
            
            lines = content.split('\n')
            title = lines[0] if lines else f"Doc {i}"
            
            documents.append("## " + content)
            ids.append(f"doc_{i}")
            metadatas.append({"title": title})

        if documents:
            try:
                self.collection.upsert(
                    documents=documents,
                    ids=ids,
                    metadatas=metadatas
                )
            except Exception as e:
                print(f"Error upserting docs: {e}", file=sys.stderr)

    def search_manual(self, query):
        """Searches the knowledge base for a solution."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=1
            )
            
            if not results['documents'] or not results['documents'][0]:
                return "No relevant info found."
                
            return results['documents'][0][0]
        except Exception as e:
            print(f"Error searching Chroma: {e}", file=sys.stderr)
            return "Search failed."
