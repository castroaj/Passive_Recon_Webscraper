from typing import Dict, Any, Tuple
import argparse
import domain_parser.domain_parser as domain_parser
import re
import logging
import yaml

VALID_EXTRACTORS = ["js", "css"]

def validate_config(yaml_config:Dict[str, Any]) -> Tuple[bool, str]:

    if "parameters" not in yaml_config:
        return False, "Configuration file is missing lvl-1 'parameters' field"

    if "log_level" not in yaml_config:
        return False, "Configuration file is missing lvl-1 'log_level' field"

    parameters:Dict[Any, Any] = yaml_config["parameters"]

    if "domain" not in parameters:
        return False, "Configuration file is missing lvl-2 'domain' field"

    if "recursive_depth" not in parameters:
        return False, "Configuration file is missing lvl-2 'recursive_depth' field"

    if "link_limit" not in parameters:
        return False, "Configuration file is missing lvl-2 'link_limit' field"

    if "file_extractors" not in parameters:
        return False, "Configuration file is missing lvl-2 'file_extraction' field"

    file_extractors:Dict[Any, Any] = parameters["file_extractors"]

    for field, value in file_extractors.items():

        if field not in VALID_EXTRACTORS:
            return False, "Configuration file does not support '" + field + "' for file_extractors"

        if "limit" not in value:
            return False, field + " must have a 'limit' to be a valid configuration"
        
    return True, "VALID"

def set_logger(log_level:str):

    if str(log_level).lower() == "info":
        logging.basicConfig(level=logging.INFO)
        return

    if str(log_level).lower() == "debug":
        logging.basicConfig(level=logging.DEBUG)
        return

    if str(log_level).lower() == "warning" or str(log_level) == "warn":
        logging.basicConfig(level=logging.WARNING)
        return

    logging.basicConfig(level=logging.INFO)
    return

def validate_domain(raw_domain:str) -> str:
    url_regex = "^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$"
    match = re.search(url_regex, raw_domain)
    
    if match is None:
        return None
    
    if str(match.string).__contains__("http://"):
        return str(match.string)
    else:
        return "http://" + str(match.string)

def main():

    # Setup an arg parser to process incoming domain
    # ==============================================
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config_file",  help="Target domain for scraping", type=str, dest="config_file")
    args = parser.parse_args()
    # ===============================================

    # Ensure the domain is provided to the application
    # ================================================
    if args.config_file is None or args.config_file == "":
        print("Configuration file must be provided")
        print("EXITING")
        exit(-1)
    # ================================================

    # Get configuration from file
    # ===========================
    with (open(args.config_file) as file_stream):
        try:
            yaml_config = yaml.safe_load(file_stream)
        except yaml.YAMLError as e:
            print(e)
            exit(-1)
    # ===========================

    # Validate the configuation file
    # ==============================
    is_valid, msg = validate_config(yaml_config=yaml_config)
    # ==============================

    # Exit if configuration file is not properly formatted
    # ====================================================
    if is_valid == False:
        print("Configuration file is invalid: " + msg)
        print("EXITING")
        exit(-1)
    # ====================================================

    # Grab the parameters
    # ===================
    config_parameters = yaml_config['parameters']
    # ===================

    # Set log level
    # =============
    set_logger(log_level=yaml_config['log_level'])
    # =============

    # Extract the domain from the args parser
    # =======================================
    processed_domain:str = validate_domain(raw_domain=config_parameters['domain'])
    # =======================================
    
    # Validate the domain matched the url expression and contains protocol header
    # ===========================================================================
    if processed_domain is None:
        print("Target domain must follow the following format: 'http://domain.extension'")
        print("EXITING")
        exit(-1)
    # ===========================================================================

    # Build out the domain parser
    # ===========================
    parser:domain_parser.Domain_Parser = domain_parser.Domain_Parser(domain=processed_domain,
                                                                     depth=config_parameters['recursive_depth'],
                                                                     link_limit=config_parameters['link_limit'],
                                                                     file_extractors=config_parameters['file_extractors'])
    # ===========================

    parser.run_file_extraction(types=list(parser.extractors.keys()))


if __name__ == "__main__":
    main()

