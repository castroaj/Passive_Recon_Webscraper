from enum import Enum
from typing import List, Dict
import os
import wget

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
    
    # Params
    # ======
    type:EXTRACTOR_TYPE
    files:Dict[str, List[str]]
    limit:int
    working_dir:str
    # ======

    # Processing DS
    # =============
    cache_dict:Dict[str, str]
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
        self.cache_dict = {}

    def run_file_extraction(self):

        if os.path.exists(self.working_dir) == False:
            os.mkdir(self.working_dir)

        if os.path.exists(self.working_dir + "/" + self.type.value[0]) == False:
            os.mkdir(self.working_dir + "/" + self.type.value[0])

        domain_id:int = 1

        for _, filenames in self.files.items():

            file_id:int = 1

            for filename in filenames:
                cache_filename:str = self.working_dir + "/" + self.type.value[0] + "/" + str(domain_id) + "_" + str(file_id) + "." + self.type.value[0]
                wget.download(filename, out=cache_filename)
                self.cache_dict[filename] = cache_filename
                file_id = file_id + 1

            domain_id = domain_id + 1
