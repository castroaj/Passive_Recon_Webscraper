from typing import List, Dict, Any, Set
import requests
import bs4
import logging
from domain_parser.extractor import EXTRACTOR, EXTRACTOR_TYPE, get_extractor_type

class Domain_Parser:
    
    logger:logging.Logger
    domain:str
    depth:int
    link_limit:int
    links:List[str]
    extractors:Dict[str, EXTRACTOR]
    cache_paths:Dict[str, Dict[str, Dict[str, str]]]
    comments:Dict[str, Dict[str, Dict[str, List[str]]]]

    def __init__(self, 
                 domain:str, 
                 link_limit:int=15, 
                 file_extractors:Dict[str, Any]={},
                 working_dir:str="./cache_data"):

        # Init class
        # ==========
        self.domain      = domain
        self.link_limit  = link_limit
        self.extractors  = {}
        self.working_dir = working_dir
        self.cache_paths = {}
        self.comments    = {}
        # ==========

        # Init logger
        # ===========
        self.logger:logging.Logger = logging.getLogger(__name__)
        self.logger.info("INITALIZING DOMAIN PARSER")
        # ===========

        # Build a list of links associated with the given domain
        # ======================================================
        self.links     = self.__ensure_pathing_includes_domain(urls=self.__pull_links_from_domain())
        # ======================================================

        # Build out extractors
        # ====================
        for type_string, params in file_extractors.items():
            extractor_type:EXTRACTOR_TYPE = get_extractor_type(type_string)
            self.extractors[extractor_type.value[0]] = self.__build_extractor(extractor_type=extractor_type, 
                                                                              limit=params['limit'])
        # ====================

    def run_file_extraction(self, types:List[str]):
        for type in types:
            self.logger.info("RUNNING FILE EXTRACTION FOR " + type + " FILETYPE")
            extractor:EXTRACTOR = self.extractors.get(type)
            extractor.run_file_extraction()
            self.cache_paths[type] = extractor.domain_paths
            print()

    def extract_comments(self, types:List[str]):
        for type in types:
            self.logger.info("EXTRACTING COMMENTS FOR " + type + " FILETYPE")
            extractor:EXTRACTOR = self.extractors.get(type)
            extractor.extract_comments_from_cache_dict()
            self.comments[type] = extractor.domain_comments

    def __pull_links_from_domain(self) -> List[str]:
        
        urls:Set[str] = set()
        urls.add(self.domain)
        
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
            urls.add(new_link)
            # =========================

        return list(urls)
        
    
    def __build_extractor(self,
                          extractor_type:EXTRACTOR_TYPE,
                          limit:int) -> EXTRACTOR:

        self.logger.info("EXTRACTING " + extractor_type.value[1] + " FILES FROM " + self.domain)
        file_dict:Dict[str, List[str]] = {}
        
        for domain in self.links:

            # Build a list of files for the filetype
            # ======================================
            domain_files:Set[str] = set()
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
                        domain_files.add(script.attrs.get("src"))
            # =================

            # HANDLE CSS
            # ==========
            elif extractor_type == EXTRACTOR_TYPE.CSS:
                for css in b_soup.find_all("link"):

                    if len(domain_files) >= limit:
                        break

                    if css.attrs.get("rel").__contains__('stylesheet'):
                        domain_files.add(css.attrs.get("href"))   
            # ==========

            file_dict[domain] = list(domain_files)

        return EXTRACTOR(type=extractor_type,
                         files=file_dict, 
                         limit=limit,
                         working_dir=self.working_dir)

    def __ensure_pathing_includes_domain(self,
                                         urls:List[str]) -> List[str]:

        processed_urls:List[str] = [self.domain]

        for url in urls:
            if url.startswith("http://") or url.startswith("https://"):
                processed_urls.append(url)
            else:
                processed_urls.append(self.domain + url)

        return list(set(processed_urls))
