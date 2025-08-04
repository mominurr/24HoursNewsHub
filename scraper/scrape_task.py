from scraper.news_scraper import scrape_all
from scraper.init_db import *

def run_scraper():
    message = scrape_all()
    return message
