import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin, urlparse
from collections import defaultdict

class WebsiteScraper:
    def __init__(self, output_dir='website_contents'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def extract_company_name(self, url: str) -> str: #function to extract company name from the url
        parsed_url = urlparse(url)
        return parsed_url.netloc.split('.')[1] if len(parsed_url.netloc.split('.')) > 1 else 'unknown_company'

    def scrape_website(self, url: str) -> str:# Function to scrape content of the website given the url
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(['script', 'style', 'head', 'meta', 'nav', 'footer']):
                script.decompose()
            text_content = soup.get_text(separator='\n', strip=True)
            text_content = re.sub(r'\n+', '\n', text_content)
            return text_content
        except requests.RequestException as e:
            print(f"Error scraping {url}: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected error scraping {url}: {e}")
            return ""

    def find_sublinks(self, base_url: str) -> list:# Function to find sublinks on the website
        try:
            response = requests.get(base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            sublinks = set()
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(base_url, href) #To get the full URL
                if self.is_valid_link(full_url, base_url):
                    sublinks.add(full_url)
            return list(sublinks)
        except requests.RequestException as e:
            print(f"Error finding sublinks on {base_url}: {e}")
            return []

    def is_valid_link(self, link: str, base_url: str) -> bool:#function to check if the link is valid or not
        parsed_base = urlparse(base_url)
        parsed_link = urlparse(link)
        return (
            parsed_link.netloc == parsed_base.netloc and #checks if the link is from the same domain
            parsed_link.scheme in ['http', 'https'] and #checks if the link is http or https
            not link.startswith('mailto:') and #checks if the link is not a mailto link
            not link.startswith('javascript:') #checks if the link is not a javascript link
            )

    def scrape_multiple_websites(self, urls: list, max_depth=1):# Function to scrape multiple websites
        company_data = defaultdict(str)
        visited_urls = set()
        for url in urls:
            try:
                company_name = self.extract_company_name(url)#getting the company name from the url
                print(f"Scraping {url}...")
                urls_to_scrape = [url]
                for depth in range(max_depth):
                    new_urls = []
                    for current_url in urls_to_scrape:
                        if current_url not in visited_urls:
                            visited_urls.add(current_url)
                            content = self.scrape_website(current_url)
                            if content:
                                company_data[company_name] += f"\n\n--- Content from {current_url} ---\n\n{content}"
                                print(f"Successfully scraped content from {current_url}.")
                            else:
                                print(f"No content found for {current_url}.")
                            if depth < max_depth - 1:#find sublinks if the depth is less than max_depth
                                new_urls.extend(self.find_sublinks(current_url))
                    urls_to_scrape = new_urls
            except Exception as e:
                print(f"Error processing {url}: {e}")

        for company_name, content in company_data.items():
            filename = f"{company_name}.txt"
            file_path = os.path.join(self.output_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Company: {company_name}\n\n")
                f.write(content)
            print(f"Saved content for {company_name} to {filename}")

def main():
    websites = [ # List of website urls to scrape
        'https://www.gm.com',
        'https://www.mobility.siemens.com',
        'https://www.alibaba.com',
        'https://www.morganstanley.com',
        'https://www.basf.com',
        'https://www.linkedin.com',
        'https://www.salesforce.com'
    ]

    scraper = WebsiteScraper(output_dir='website_contents') # Create an instance of WebsiteScraper class
    scraper.scrape_multiple_websites(websites, max_depth=2)  # Scrape the websites with a maximum depth of 2

if __name__ == "__main__":
    main()