from enum import Enum
from typing import List, Dict
import os
import wget
import re
import logging

class EXTRACTOR_TYPE(Enum):
    JS = ("js", "JAVASCRIPT", ".*")
    CSS = ("css", "CSS (Cascading Style Sheets)", ".*")

def get_extractor_type(type_string:str) -> EXTRACTOR_TYPE:

    if type_string == EXTRACTOR_TYPE.JS.value[0]:
        return EXTRACTOR_TYPE.JS
    
    if type_string == EXTRACTOR_TYPE.CSS.value[0]:
        return EXTRACTOR_TYPE.CSS
    
    return None

class EXTRACTOR():
    
    # Params
    # ======
    type:EXTRACTOR_TYPE
    files:Dict[str, List[str]]
    limit:int
    working_dir:str
    # ======

    # Processing DS
    # =============
    domain_paths:Dict[str, Dict[str, str]]
    domain_comments:Dict[str, Dict[str, List[str]]]
    # =============

    def __init__(self,
                 type:EXTRACTOR_TYPE,
                 files:Dict[str, List[str]],
                 limit:int,
                 working_dir:str):

        self.type  = type
        self.files = files
        self.limit = limit
        self.working_dir = working_dir

        self.domain_paths = {}
        self.domain_comments = {}

        self.logger:logging.Logger = logging.getLogger(__name__)
        self.logger.info("INITALIZING EXTRACTOR FOR " + type.value[1] + " FILETYPE")

    def run_file_extraction(self):

        if os.path.exists(self.working_dir) == False:
            os.mkdir(self.working_dir)

        if os.path.exists(self.working_dir + "/" + self.type.value[0]) == False:
            os.mkdir(self.working_dir + "/" + self.type.value[0])

        domain_id:int = 1

        for domain, filenames in self.files.items():

            self.domain_paths[domain] = {}
            file_id:int = 1

            for filename in filenames:
                cache_filename:str = self.working_dir + "/" + self.type.value[0] + "/" + str(domain_id) + "_" + str(file_id) + "." + self.type.value[0]
                
                try:
                    wget.download(filename, out=cache_filename)
                except:
                    print()
                    self.logger.error("FAILED TO DOWNLOAD FILE: " + filename)
                    print()
                    continue

                self.domain_paths[domain][filename] = cache_filename
                file_id = file_id + 1

            domain_id = domain_id + 1

    def extract_comments_from_cache_dict(self):
        
        for domain, paths in self.domain_paths.items():
            self.domain_comments[domain] = {}
            for filename, path in paths.items():

                # Read all of the file data
                # =========================
                file_data:str
                with open(path, "r") as file:
                    file_data = file.read()
                # =========================

                self.domain_comments[domain][filename] = re.findall(self.type.value[2], file_data)


