import argparse
import requests
import bs4
import domain_parser
import re

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
    parser.add_argument("-d", "--domain",  help="Target domain for scraping", type=str, dest="domain")
    args = parser.parse_args()
    # ===============================================

    # Ensure the domain is provided to the application
    # ================================================
    if args.domain is None or args.domain == "":
        print("Target domain required as first arguement")
        print("EXITING")
        exit(0)
    # ================================================

    # Extract the domain from the args parser
    # =======================================
    domain:str = validate_domain(raw_domain=args.domain)
    # =======================================
    
    # Validate the domain matched the url expression and contains protocol header
    # ===========================================================================
    if domain is None:
        print("Target domain must follow the following format: 'http://domain.extension'")
    # ===========================================================================

    parser:domain_parser.Domain_Parser = domain_parser.Domain_Parser(domain=domain)

    print(parser.links)    


if __name__ == "__main__":
    main()

