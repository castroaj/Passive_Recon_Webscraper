from typing import List
import requests
import bs4

class Domain_Parser:
    
    domain:str
    depth:int
    links:List[str]
    js_files:List[str]
    css_files:List[str]
    
    def __init__(self, domain:str, depth:int=1):
        self.domain    = domain
        self.depth     = depth

        self.links     = self.pull_links_from_domain()
        self.js_files  = self.pull_js_urls_from_domain(domains=self.links)    
        self.css_files = self.pull_css_urls_from_domain(domains=self.links)
   
    def pull_links_from_domain(self):
        
        urls:List[str] = []
        
        response:requests.Response = requests.get(self.domain)
        b_soup:bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
        
        for link in b_soup.find_all("a"):
            urls.append(link.get("href"))
            
        return urls
        
    
    def pull_js_urls_from_domain(self, domains:List[str]) -> List[str]:
        
        js_files:List[str] = []
        
        for domain in domains:
            response:requests.Response = requests.get(domain)
            b_soup:bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
        
            for script in b_soup.find_all("script"):
                if script.attrs.get("src"):
                    js_files.append(script.attrs.get("src"))
                
        return js_files

    def pull_css_urls_from_domain(self, domains:List[str]) -> List[str]:
        
        css_files:List[str] = []
       
        for domain in domains: 
            response:requests.Response = requests.get(domain)
            b_soup:bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
        
            for css in b_soup.find_all("link"):
                if css.attrs.get("href"):
                    css_files.append(css.attrs.get("href"))        
        
        return css_files 