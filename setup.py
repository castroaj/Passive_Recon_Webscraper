from setuptools import setup, find_packages

setup(
    name='domain_parser',
    version='1.0.0',
    url='https://github.com/castroaj/Passive_Recon_Webscraper.git',
    author='Alexander Castro',
    author_email='Alexcast129@gmail.com',
    description='Description of my package',
    packages=find_packages(),    
    install_requires=['bs4', 'wget'],
)