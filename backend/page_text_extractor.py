#!/usr/bin/env python3
"""
Script to extract and display all text content from AnNisa.org pages.
This helps you see what text is available on each page for the chatbot.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
import os

class PageTextExtractor:
    def __init__(self, base_url="https://annisa.org"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Common pages to check
        self.pages_to_check = [
            "",  # Home page
            "/about",
            "/services", 
            "/programs",
            "/volunteer",
            "/donate",
            "/contact",
            "/events",
            "/resources",
            "/news",
            "/blog",
            "/team",
            "/mission",
            "/get-involved",
            "/community"
        ]

    def clean_text(self, text):
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
        # Remove extra spaces again
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def extract_text_from_url(self, url):
        """Extract all meaningful text from a given URL."""
        print(f"🔍 Checking: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 404:
                print(f"   ❌ Page not found (404)")
                return None
            elif response.status_code != 200:
                print(f"   ❌ Error {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract text from main content areas
            text_elements = []
            
            # Try to find main content areas
            main_selectors = [
                'main', '[role="main"]', '.main-content', '#main', 
                '.content', '.page-content', 'article', '.post-content'
            ]
            
            main_content = None
            for selector in main_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if main_content:
                # Extract from main content area
                for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div']):
                    text = element.get_text(strip=True)
                    if text and len(text) > 20:  # Only meaningful text
                        text_elements.append(text)
            else:
                # Fallback: extract from body
                body = soup.find('body')
                if body:
                    for element in body.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                        text = element.get_text(strip=True)
                        if text and len(text) > 20:
                            text_elements.append(text)
            
            # Join and clean all text
            full_text = ' '.join(text_elements)
            cleaned_text = self.clean_text(full_text)
            
            # Get page title
            title = soup.find('title')
            page_title = title.get_text(strip=True) if title else "No title"
            
            print(f"   ✅ Found {len(cleaned_text)} characters")
            
            return {
                'url': url,
                'title': page_title,
                'text': cleaned_text,
                'word_count': len(cleaned_text.split()),
                'char_count': len(cleaned_text)
            }
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None

    def extract_all_pages(self):
        """Extract text from all pages and display results."""
        print("🚀 Starting text extraction from AnNisa.org pages")
        print("=" * 70)
        
        results = []
        
        for page_path in self.pages_to_check:
            url = urljoin(self.base_url, page_path)
            result = self.extract_text_from_url(url)
            
            if result:
                results.append(result)
            
            # Be respectful with timing
            time.sleep(1)
        
        print("\n" + "=" * 70)
        print("📊 EXTRACTION RESULTS SUMMARY")
        print("=" * 70)
        
        if not results:
            print("❌ No content was successfully extracted from any pages.")
            return
        
        # Sort by content length (most content first)
        results.sort(key=lambda x: x['char_count'], reverse=True)
        
        total_chars = sum(r['char_count'] for r in results)
        total_words = sum(r['word_count'] for r in results)
        
        print(f"✅ Successfully extracted from {len(results)} pages")
        print(f"📝 Total content: {total_chars:,} characters, {total_words:,} words")
        print()
        
        # Display each page's content
        for i, result in enumerate(results, 1):
            print(f"[{i}] {result['url']}")
            print(f"    📄 Title: {result['title']}")
            print(f"    📊 Stats: {result['char_count']:,} chars, {result['word_count']:,} words")
            print(f"    📝 Preview: {result['text'][:200]}...")
            print()
        
        # Save detailed results to file
        self.save_results_to_file(results)
        
        return results

    def save_results_to_file(self, results):
        """Save detailed text extraction results to a file."""
        output_file = "data/page_text_extraction.txt"
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("AnNisa.org Page Text Extraction Results\n")
                f.write("=" * 50 + "\n\n")
                
                for i, result in enumerate(results, 1):
                    f.write(f"[{i}] {result['url']}\n")
                    f.write(f"Title: {result['title']}\n")
                    f.write(f"Characters: {result['char_count']:,}\n")
                    f.write(f"Words: {result['word_count']:,}\n")
                    f.write("-" * 50 + "\n")
                    f.write(result['text'])
                    f.write("\n\n" + "=" * 50 + "\n\n")
            
            print(f"💾 Detailed results saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")

    def show_page_content(self, page_path=""):
        """Show detailed content from a specific page."""
        url = urljoin(self.base_url, page_path)
        result = self.extract_text_from_url(url)
        
        if result:
            print(f"\n📄 CONTENT FROM: {result['url']}")
            print(f"🏷️  Title: {result['title']}")
            print(f"📊 Stats: {result['char_count']} chars, {result['word_count']} words")
            print("-" * 50)
            print(result['text'])
            print("-" * 50)
        else:
            print(f"❌ Could not extract content from {url}")

def main():
    """Main function to run the text extractor."""
    extractor = PageTextExtractor()
    
    print("🌐 AnNisa.org Page Text Extractor")
    print("This script will check all pages and show what text is available.")
    print()
    
    # Extract from all pages
    results = extractor.extract_all_pages()
    
    # Option to view specific page content
    print("\n" + "=" * 70)
    print("💡 To see full content from a specific page, uncomment one of these lines:")
    print("   # extractor.show_page_content('')        # Home page")
    print("   # extractor.show_page_content('/about')  # About page")
    print("   # extractor.show_page_content('/donate') # Donate page")

if __name__ == "__main__":
    main() 