all: clean install run

install:
	pip3 install .

run:
	python3 passive_recon_webscraper.py -c configuration.yml

clean: 
	rm -drf cache_data build domain_parser.egg-info;