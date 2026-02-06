from sentence_transformers import SentenceTransformer
print("Loading model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded.")
print("-" * 20)
print(model.encode("test"))
print("Done.")
