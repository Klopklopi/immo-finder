import time
import logging
import settings
from app.utils import logger as log
from app.scrapers import seloger,pap

def timed_job():
    log.init_logging()
    logger = logging.getLogger()
    logger.info("{}: Starting scrape cycle".format(time.ctime()))
    
    # Initialize scraper and get offers
    scraper = pap.Pap()
    all_offers = []
    
    # Use the _next_page method to get all offers
    try:
        for page_offers in scraper._next_page():
            all_offers.extend(page_offers)
            logger.info(f"Found {len(page_offers)} offers on this page")
            break  # Just check first page for now
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        logger.info(f"Partial results: {len(all_offers)} offers found before error")
    
    logger.info(f"Total offers found: {len(all_offers)}")
    
    # Print all offers
    for i, offer in enumerate(all_offers, 1):
        print(f"\n=== Offre {i} ===")
        print(f"Titre: {offer.title}")
        print(f"Prix: {offer.price}€")
        print(f"Surface: {offer.surface}m²")
        print(f"URL: {offer.details_url}")
        if offer.description:
            print(f"Description: {offer.description[:200]}...")
    
    logger.info("{}: Successfully finished scraping".format(time.ctime()))

timed_job()
