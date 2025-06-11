#!/usr/bin/env python3
"""
Flask backend for AnNisa.org AI chatbot.
Provides RAG (Retrieval Augmented Generation) capabilities using embeddings and OpenAI.
"""

import os
import pickle
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import openai
from dotenv import load_dotenv
import logging
from typing import List, Dict

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnNisaChatbot:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunks = []
        self.embeddings = None
        self.metadata = []
        self.openai_client = None
        
        self.load_knowledge_base()
        self.setup_openai()
    
    def load_knowledge_base(self):
        """Load knowledge base from pickle file."""
        try:
            if os.path.exists("data/knowledge_base.pkl"):
                with open("data/knowledge_base.pkl", "rb") as f:
                    knowledge_base = pickle.load(f)
                    self.chunks = knowledge_base['chunks']
                    self.embeddings = knowledge_base['embeddings']
                    self.metadata = knowledge_base['metadata']
                
                logger.info(f"Loaded knowledge base with {len(self.chunks)} chunks")
            else:
                logger.error("Knowledge base not found! Run ingest.py first.")
                
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
            logger.error("Make sure to run ingest.py first to create the knowledge base.")
    
    def setup_openai(self):
        """Setup OpenAI client."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment variables!")
            return
        
        openai.api_key = api_key
        self.openai_client = openai
        logger.info("OpenAI client initialized")
    
    def search_knowledge_base(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant chunks in the knowledge base."""
        if self.embeddings is None or len(self.chunks) == 0:
            return []
        
        try:
            # Embed the query
            query_embedding = self.model.encode([query])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Format results
            results = []
            for i, idx in enumerate(top_indices):
                if similarities[idx] > 0.1:  # Only include relevant chunks
                    results.append({
                        'content': self.chunks[idx],
                        'metadata': self.metadata[idx],
                        'score': float(similarities[idx]),
                        'rank': i + 1
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []
    
    def generate_response(self, query: str, context_chunks: List[Dict]) -> str:
        """Generate response using OpenAI GPT with retrieved context."""
        if not self.openai_client:
            return "Sorry, I'm having trouble connecting to the AI service. Please try again later."
        
        try:
            # Prepare context from retrieved chunks
            context_text = ""
            sources = set()
            
            for chunk in context_chunks:
                context_text += f"Content: {chunk['content']}\n"
                context_text += f"Source: {chunk['metadata']['url']}\n\n"
                sources.add(chunk['metadata']['url'])
            
            # Create the prompt
            system_prompt = """You are Amal, a compassionate assistant for An-Nisa Hope Center. 
            You answer questions based only on the provided context from the AnNisa.org website.
            
            Guidelines:
            - Only use information from the provided context
            - If you can't answer based on the context, say so politely
            - When relevant, include specific page links naturally within your response (e.g., "You can learn more at https://annisa.org/programs")
            - Be helpful, caring, and informative
            - Keep responses warm but concise
            - Don't mention "based on the context" - just answer conversationally
            - Speak in first person as Amal
            - Be very caring and compassionate, emphasize hope
            - Include relevant URLs naturally in your response when they would be helpful
           """
            
            user_prompt = f"""Context from AnNisa.org:
            {context_text}
            
            Question: {query}
            
            Please answer as Amal, including any relevant page URLs naturally in your response when they would be helpful to the person asking."""
            
            # Call OpenAI API
            response = self.openai_client.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I'm having some technical difficulties right now. Please try asking your question again, or visit annisa.org for more information."

# Initialize chatbot
chatbot = AnNisaChatbot()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'AnNisa Chatbot API',
        'knowledge_base_loaded': len(chatbot.chunks) > 0,
        'chunks_count': len(chatbot.chunks)
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint."""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        logger.info(f"Received query: {user_message}")
        
        # Search knowledge base
        relevant_chunks = chatbot.search_knowledge_base(user_message, top_k=3)
        
        if not relevant_chunks:
            return jsonify({
                'response': "I don't have specific information about that topic. For the most up-to-date details, I'd recommend visiting annisa.org directly or reaching out to them - they'll be happy to help!"
            })
        
        # Generate response
        response = chatbot.generate_response(user_message, relevant_chunks)
        
        return jsonify({
            'response': response,
            'chunks_used': len(relevant_chunks)
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/search', methods=['POST'])
def search():
    """Search endpoint for debugging."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        chunks = chatbot.search_knowledge_base(query, top_k=5)
        
        return jsonify({
            'query': query,
            'results': chunks
        })
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Check if knowledge base exists
    if not os.path.exists("data/knowledge_base.pkl"):
        print("❌ Knowledge base not found!")
        print("Please run 'python ingest.py' first to create the knowledge base.")
        exit(1)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found!")
        print("Please add your OpenAI API key to the .env file.")
        exit(1)
    
    logger.info("🚀 Starting AnNisa Chatbot API...")
    logger.info("📚 Knowledge base loaded")
    logger.info("🤖 OpenAI integration ready")
    
    # Use environment port for production or default to 5001 for local development
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"🌐 Server running on port {port}")
    
    app.run(debug=False, host='0.0.0.0', port=port) 