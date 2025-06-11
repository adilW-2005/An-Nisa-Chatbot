#!/usr/bin/env python3
"""
Script to inspect the contents of the knowledge base PKL file.
Shows what data is actually stored and how it's structured.
"""

import pickle
import numpy as np
import os

def inspect_knowledge_base():
    """Inspect and display knowledge base contents."""
    pkl_path = "data/knowledge_base.pkl"
    
    if not os.path.exists(pkl_path):
        print(f"❌ Knowledge base not found at {pkl_path}")
        print("Run ingest.py first to create it!")
        return
    
    print(f"🔍 Inspecting: {pkl_path}")
    print("=" * 60)
    
    try:
        # Load the PKL file
        with open(pkl_path, "rb") as f:
            knowledge_base = pickle.load(f)
        
        print("📦 KNOWLEDGE BASE STRUCTURE:")
        print(f"   Type: {type(knowledge_base)}")
        print(f"   Keys: {list(knowledge_base.keys())}")
        print()
        
        # Inspect chunks
        chunks = knowledge_base.get('chunks', [])
        print(f"📝 CHUNKS ({len(chunks)} total):")
        for i, chunk in enumerate(chunks[:3]):  # Show first 3
            print(f"   [{i}] Length: {len(chunk)} chars")
            print(f"       Preview: \"{chunk[:100]}...\"")
        if len(chunks) > 3:
            print(f"   ... and {len(chunks) - 3} more chunks")
        print()
        
        # Inspect embeddings
        embeddings = knowledge_base.get('embeddings', [])
        if len(embeddings) > 0:
            embeddings_array = np.array(embeddings)
            print(f"🧠 EMBEDDINGS:")
            print(f"   Shape: {embeddings_array.shape}")
            print(f"   Type: {embeddings_array.dtype}")
            print(f"   Sample values from first embedding:")
            print(f"   {embeddings_array[0][:10]}...")  # First 10 values
        print()
        
        # Inspect metadata
        metadata = knowledge_base.get('metadata', [])
        print(f"📊 METADATA ({len(metadata)} entries):")
        for i, meta in enumerate(metadata[:3]):  # Show first 3
            print(f"   [{i}] {meta}")
        if len(metadata) > 3:
            print(f"   ... and {len(metadata) - 3} more entries")
        print()
        
        # Summary statistics
        print("📈 SUMMARY STATISTICS:")
        if chunks:
            avg_chunk_length = sum(len(chunk) for chunk in chunks) / len(chunks)
            print(f"   Average chunk length: {avg_chunk_length:.1f} characters")
        
        if embeddings:
            print(f"   Embedding dimensions: {len(embeddings[0])}")
            print(f"   Total vectors: {len(embeddings)}")
        
        # File size
        file_size = os.path.getsize(pkl_path)
        print(f"   File size: {file_size / 1024 / 1024:.2f} MB")
        
        print("=" * 60)
        print("✅ Knowledge base inspection complete!")
        
    except Exception as e:
        print(f"❌ Error reading PKL file: {e}")

def test_similarity_search():
    """Test how similarity search works with the data."""
    pkl_path = "data/knowledge_base.pkl"
    
    if not os.path.exists(pkl_path):
        print("❌ No knowledge base to test with!")
        return
    
    print("\n🔬 TESTING SIMILARITY SEARCH:")
    print("=" * 60)
    
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Load knowledge base
        with open(pkl_path, "rb") as f:
            kb = pickle.load(f)
        
        chunks = kb['chunks']
        embeddings = np.array(kb['embeddings'])
        metadata = kb['metadata']
        
        # Load the same model used for embeddings
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Test query
        test_query = "What does AnNisa do?"
        print(f"🔍 Test Query: \"{test_query}\"")
        
        # Embed the query
        query_embedding = model.encode([test_query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_embedding, embeddings)[0]
        
        # Get top 3 matches
        top_indices = np.argsort(similarities)[-3:][::-1]
        
        print(f"\n📋 TOP 3 MATCHES:")
        for i, idx in enumerate(top_indices):
            print(f"\n   [{i+1}] Similarity Score: {similarities[idx]:.4f}")
            print(f"       Source: {metadata[idx]['url']}")
            print(f"       Content: \"{chunks[idx][:200]}...\"")
        
        print("\n✅ Similarity search test complete!")
        
    except Exception as e:
        print(f"❌ Error testing similarity search: {e}")

if __name__ == "__main__":
    inspect_knowledge_base()
    test_similarity_search() 