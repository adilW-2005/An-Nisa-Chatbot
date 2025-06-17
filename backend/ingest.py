#!/usr/bin/env python3
"""
Web scraping and content ingestion script for AnNisa.org chatbot.
Crawls key pages, chunks content, creates embeddings, and stores them.
"""

import os
import requests
from bs4 import BeautifulSoup
import pickle
import re
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class AnNisaContentIngester:
    def __init__(self):
        self.base_url = "https://annisa.org"
        # Use the same smaller, optimized model as in app.py
        # paraphrase-MiniLM-L3-v2: ~14MB, optimized for CPU, ~95% performance
        self.model = SentenceTransformer('paraphrase-MiniLM-L3-v2', device='cpu')
        self.chunks = []
        self.embeddings = []
        self.metadata = []
        
        # Key pages to crawl
        self.target_pages = [
            "/",
            "/about",
            "/services",
            "/mental-health",
            "/blog",
            "/advocacy", 
            "/food-pantry",
            "/donate",
            "/volunteer",
            "/about-us",
            "/team",
            "/gallery",
            "/contact-us",
            "/roadmap",
            "/family-violence",
            "/ecrf",
        ]
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        return text.strip()
    
    def extract_content(self, url: str) -> Dict[str, str]:
        """Extract content from a single page."""
        try:
            print(f"Scraping: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text() if title else ""
            
            # Extract main content
            content_selectors = [
                'main', 'article', '.content', '#content', 
                '.main-content', '.page-content', 'section'
            ]
            
            content_text = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content_text = content_elem.get_text()
                    break
            
            # Fallback to body if no specific content area found
            if not content_text:
                content_text = soup.body.get_text() if soup.body else soup.get_text()
            
            # Clean the content
            clean_content = self.clean_text(content_text)
            
            return {
                'url': url,
                'title': self.clean_text(title_text),
                'content': clean_content
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.strip()) > 50:  # Only keep substantial chunks
                chunks.append(chunk)
        
        return chunks
    
    def scrape_all_pages(self):
        """Scrape all target pages and create chunks."""
        print("Starting content ingestion for AnNisa.org...")
        
        for page_path in self.target_pages:
            url = urljoin(self.base_url, page_path)
            content_data = self.extract_content(url)
            
            if content_data and content_data['content']:
                # Create chunks from the content
                text_chunks = self.chunk_text(content_data['content'])
                
                for i, chunk in enumerate(text_chunks):
                    self.chunks.append(chunk)
                    self.metadata.append({
                        'url': content_data['url'],
                        'title': content_data['title'],
                        'chunk_id': i,
                        'source': 'annisa.org'
                    })
                
                print(f"  → Added {len(text_chunks)} chunks from {url}")
            
            # Be respectful with requests
            time.sleep(1)
        
        print(f"\nTotal chunks collected: {len(self.chunks)}")
    
    def create_embeddings(self):
        """Create embeddings for all chunks."""
        print("Creating embeddings...")
        
        if not self.chunks:
            print("No chunks to embed!")
            return
        
        # Create embeddings
        self.embeddings = self.model.encode(self.chunks, show_progress_bar=True)
        print(f"Created embeddings shape: {self.embeddings.shape}")
    
    def save_knowledge_base(self):
        """Save knowledge base to files."""
        print("Saving knowledge base...")
        
        # Save the knowledge base
        knowledge_base = {
            'chunks': self.chunks,
            'embeddings': self.embeddings,
            'metadata': self.metadata
        }
        
        with open("data/knowledge_base.pkl", "wb") as f:
            pickle.dump(knowledge_base, f)
        
        print(f"Knowledge base saved with {len(self.chunks)} chunks")
        print("Knowledge base created successfully!")
    
    def add_google_forms_info(self):
        """Add information about important Google Forms that users should know about."""
        
        # Volunteer Form Information
        volunteer_form_text = """
        An-Nisa Volunteer Opportunities - Join Our Team!
        
        We welcome volunteers to join our mission of supporting women and families. We have volunteer opportunities in multiple departments:
        
        Volunteer Departments Available:
        - Education
        - Mental Health  
        - Advocacy & Legislation
        - Administration
        - Marketing
        - Mentorship
        - Events
        - Youth Programs
        
        To volunteer with An-Nisa, please fill out our volunteer application form. The form asks for:
        - Your contact information
        - Education level
        - Which department you're interested in
        - Why you want to volunteer
        - How many hours you can commit per week
        - What skills and services you can offer
        
        Once you submit the form, a staff member will follow up with the volunteer on-boarding process.
        
        Apply to volunteer: https://docs.google.com/forms/d/e/1FAIpQLSdska_omS24UValnvU5wlWxcQjI9TynfDbJJa9KkgbRUHvztA/viewform
        
        For more information about volunteering, email info@annisa.org
        """
        
        # DV Assistance Form Information  
        dv_assistance_text = """
        Domestic Violence Assistance and Support Services
        
        An-Nisa provides confidential support and assistance for individuals experiencing domestic violence. We understand that seeking help can be difficult, and we're here to support you through this process.
        
        If you or someone you know needs domestic violence assistance, we have a confidential intake form available. This form allows you to request support services safely and privately.
        
        Our domestic violence support services may include:
        - Safety planning
        - Resource referrals
        - Advocacy support
        - Connection to local services
        - Emotional support
        
        To request domestic violence assistance confidentially: https://docs.google.com/forms/d/e/1FAIpQLSfA9R_H1KDM5AHDbZ82HczE8oq6XxpiH_Z17BK5PGwLdQBCjQ/viewform
        
        For immediate safety concerns, please contact local emergency services at 911.
        For additional support, you can also email info@annisa.org
        """
        
        # Add these as chunks
        self.chunks.append(volunteer_form_text.strip())
        self.metadata.append({
            'url': 'https://docs.google.com/forms/d/e/1FAIpQLSdska_omS24UValnvU5wlWxcQjI9TynfDbJJa9KkgbRUHvztA/viewform',
            'title': 'An-Nisa Volunteer Application Form',
            'type': 'volunteer_form'
        })
        
        self.chunks.append(dv_assistance_text.strip())  
        self.metadata.append({
            'url': 'https://docs.google.com/forms/d/e/1FAIpQLSfA9R_H1KDM5AHDbZ82HczE8oq6XxpiH_Z17BK5PGwLdQBCjQ/viewform',
            'title': 'An-Nisa Domestic Violence Assistance Form',
            'type': 'assistance_form'
        })
        
        print(f"✅ Added volunteer and DV assistance form information")

    def process_urls(self):
        """Process all URLs and create knowledge base."""
        print("🚀 Starting AnNisa.org content ingestion...")
        print("=" * 60)
        
        # Process regular website pages using existing method
        self.scrape_all_pages()
        
        # Add Google Forms information
        self.add_google_forms_info()
        
        print(f"\n📊 INGESTION COMPLETE")
        print("=" * 60)
        print(f"✅ Total chunks created: {len(self.chunks)}")
        print(f"📄 Total pages processed: {len(set(meta['url'] for meta in self.metadata))}")
        
        if len(self.chunks) == 0:
            print("❌ No content was extracted! Check the URLs and try again.")
            return False
        
        return True

if __name__ == "__main__":
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Initialize scraper
    scraper = AnNisaContentIngester()
    
    # Process all content
    success = scraper.process_urls()
    
    if not success:
        print("❌ Failed to create knowledge base!")
        exit(1)
    
    # Create embeddings and save
    scraper.create_embeddings()
    scraper.save_knowledge_base()
    
    print("\nIngestion complete! Knowledge base ready for chatbot.")
    print("Knowledge base saved as ./data/knowledge_base.pkl") 