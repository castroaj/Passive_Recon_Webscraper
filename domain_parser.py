from typing import List, Dict, Any
from enum import Enum
import requests
import bs4
import logging

class EXTRACTOR_TYPE(Enum):
    JS = ("js", "JAVASCRIPT")
    CSS = ("css", "CSS (Cascading Style Sheets)")


def get_extractor_type(type_string:str) -> EXTRACTOR_TYPE:

    if type_string == EXTRACTOR_TYPE.JS.value[0]:
        return EXTRACTOR_TYPE.JS
    
    if type_string == EXTRACTOR_TYPE.CSS.value[0]:
        return EXTRACTOR_TYPE.CSS
    
    return None

class EXTRACTOR():
    
    type:EXTRACTOR_TYPE
    files:Dict[str, List[str]]
    limit:int
    regex:str

    def __init__(self,
                 type:EXTRACTOR_TYPE,
                 files:Dict[str, List[str]],
                 limit:int,
                 regex:str):

        self.type  = type
        self.files = files
        self.limit = limit
        self.regex = regex


class Domain_Parser:
    
    logger:logging.Logger
    domain:str
    depth:int
    link_limit:int
    links:List[str]
    extractors:Dict[EXTRACTOR_TYPE, EXTRACTOR]

    def __init__(self, 
                 domain:str, 
                 depth:int=1, 
                 link_limit:int=15, 
                 file_extractors:Dict[str, Any]={}):

        # Init class
        # ==========
        self.domain         = domain
        self.depth          = depth
        self.link_limit     = link_limit
        self.extractors = {}
        # ==========

        # Init logger
        # ===========
        self.logger:logging.Logger = logging.getLogger(__name__)
        self.logger.info("INITALIZING DOMAIN PARSER")
        # ===========

        # Build a list of links associated with the given domain
        # ======================================================
        self.links     = self.__ensure_pathing_includes_domain(urls=self.pull_links_from_domain())
        # ======================================================

        # Build out extractors
        # ====================
        for type_string, params in file_extractors.items():
            extractor_type:EXTRACTOR_TYPE = get_extractor_type(type_string)
            self.extractors[extractor_type] = self.build_extractor(extractor_type=extractor_type, 
                                                                   limit=params['limit'],
                                                                   regex=params['regex'])
        # ====================


    def pull_links_from_domain(self) -> List[str]:
        """
        Extract any linked files from the user provided domain

        return : a list of linked files
        """
        
        urls:List[str] = [self.domain]
        
        self.logger.info("EXTRACTING LINKS FROM " + self.domain)

        response:requests.Response = requests.get(self.domain)
        b_soup:bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
        
        for link in b_soup.find_all("a"):

            if len(urls) >= self.link_limit:
                break
            
            # Extract and store newlink
            # =========================
            new_link:str = link.get("href")
            self.logger.debug(new_link + " has been found")
            urls.append(new_link)
            # =========================

        return urls
        
    
    def build_extractor(self,
                        extractor_type:EXTRACTOR_TYPE,
                        limit:int,
                        regex:str) -> EXTRACTOR:

        self.logger.info("EXTRACTING " + extractor_type.value[1] + " FILES FROM " + self.domain)
        file_dict:Dict[str, List[str]] = {}
        
        for domain in self.links:

            # Build a list of files for the filetype
            # ======================================
            domain_files:List[str] = []
            # ======================================

            # Retrieve file data from the domain and build an html parser for it
            # ==================================================================
            self.logger.debug("PROCESSING " + domain)
            response:requests.Response = requests.get(domain)
            b_soup:bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
            # ==================================================================

            # HANDLE JAVASCRIPT
            # =================
            if extractor_type == EXTRACTOR_TYPE.JS:
                for script in b_soup.find_all("script"):

                    if len(domain_files) >= limit:
                        break

                    if script.attrs.get("src"):
                        domain_files.append(script.attrs.get("src"))
            # =================

            # HANDLE CSS
            # ==========
            elif extractor_type == EXTRACTOR_TYPE.CSS:
                for css in b_soup.find_all("link"):

                    if len(domain_files) >= limit:
                        break

                    if css.attrs.get("rel").__contains__('stylesheet'):
                        domain_files.append(css.attrs.get("href"))   
            # ==========

            file_dict[domain] = domain_files

        return EXTRACTOR(type=extractor_type,
                         files=file_dict, 
                         limit=limit, 
                         regex=regex)

    def __ensure_pathing_includes_domain(self,
                                         urls:List[str]) -> List[str]:

        processed_urls:List[str] = [self.domain]

        for url in urls:
            if url.startswith("http://") or url.startswith("https://"):
                processed_urls.append(url)
            else:
                processed_urls.append(self.domain + url)

        return list(set(processed_urls))
