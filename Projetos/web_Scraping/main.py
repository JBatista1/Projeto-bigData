import os
from selenium import webdriver
from download_manager import DownloadManager
from zip_extractor import ZipExtractor
from scraper import Scraper

def main():
    download_dir = os.path.join(os.getcwd(), "cvs")
    os.makedirs(download_dir, exist_ok=True)

    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    download_manager = DownloadManager(download_dir)
    zip_extractor = ZipExtractor()
    url = "https://dados.gov.br/dados/conjuntos-dados/serie-historica-de-precos-de-combustiveis-e-de-glp"
    scraper = Scraper(download_manager, zip_extractor, url, chrome_options)

    scraper.inicia_scraping()

if __name__ == '__main__':
    main()
