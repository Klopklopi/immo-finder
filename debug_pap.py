#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

# Test the PAP URL directly
url = "https://www.pap.fr/annonce/location-appartement-nantes-44-g43619-jusqu-a-2000-euros-a-partir-de-20-m2-1"

print(f"Testing URL: {url}")

try:
    # Get the page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try original selector
        item_titles = soup.find_all(lambda tag: tag.has_attr('class') and tag['class'] == ['item-title'])
        print(f"Found {len(item_titles)} elements with class 'item-title'")
        
        # Try alternative selectors
        alt_selectors = [
            "div.item-title",
            ".item-title", 
            "h2",
            "h3", 
            "a[title]",
            ".item",
            ".listing-item",
            ".search-list-item"
        ]
        
        for selector in alt_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    # Print first few elements for inspection
                    for i, elem in enumerate(elements[:3]):
                        print(f"  Element {i+1}: {str(elem)[:100]}...")
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                
        # Print page title and a sample of content
        title = soup.find('title')
        if title:
            print(f"Page title: {title.text.strip()}")
            
        # Look for any elements that might contain listings
        content_divs = soup.find_all('div', class_=lambda x: x and 'search' in str(x).lower())
        print(f"Found {len(content_divs)} divs with 'search' in class name")
        
    else:
        print(f"Failed to fetch page: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"Error: {e}")