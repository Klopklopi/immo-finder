# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Python-based real estate scraper bot designed to find apartments for sale in Paris based on configurable criteria. The bot is extensible and originally designed to deploy on Heroku with Slack notifications. It scrapes multiple real estate websites (Bien Ici, PAP, Se Loger) and filters results based on price, surface area, location, and content criteria.

## Architecture

### Core Components

- **Models (`app/models/`)**: Data structures for real estate offers
  - `BaseOffer`: Abstract base class with common properties (price, surface, description, etc.)
  - `ApartmentOffer`, `CommerceOffer`: Specific offer types extending BaseOffer

- **Scrapers (`app/scrapers/`)**: Web scraping implementations
  - `BaseScraper`: Abstract base class using Selenium WebDriver with template method pattern
  - `BienIci`, `Pap`, `SeLoger`: Concrete scraper implementations for each real estate site
  - Uses PhantomJS (headless browser) for web scraping with BeautifulSoup for HTML parsing

- **Services (`app/services/`)**: Business logic
  - `Filter`: Applies configurable filtering rules to exclude irrelevant offers

- **Configuration (`config/`)**: Environment-based configuration modules
  - `core.py`: System settings (database URL, logging, sleep intervals)
  - `filtering.py`: Content and pricing filter parameters
  - Site-specific configs: `bienici.py`, `pap.py`, `seloger.py`

### Design Patterns

- **Template Method Pattern**: `BaseScraper` defines scraping workflow, subclasses implement site-specific details
- **Strategy Pattern**: Each scraper implements different extraction strategies for their respective sites
- **Configuration via Environment Variables**: All settings configurable through environment variables

## Common Commands

### Running the Application

```bash
# Run main scraping script (currently only SeLoger active)
python main.py

# Run full scraping cycle (PAP and SeLoger)
python scrape.py
```

### Development Workflow

```bash
# Install dependencies (legacy requirements.txt)
pip install -r requirements.txt

# Install with uv (modern approach)
uv sync

# Run tests
python -m unittest discover tests/

# Run specific test
python -m unittest tests.utils.test_offer

# Run individual test methods
python -m unittest tests.utils.test_offer.OfferTestCase.test_price
```

### Project Structure

```
immo-finder/
├── app/
│   ├── models/          # Data models (BaseOffer, ApartmentOffer, etc.)
│   ├── scrapers/        # Web scraping implementations
│   ├── services/        # Business logic (filtering)
│   └── utils/           # Utilities (logging)
├── config/              # Configuration modules
├── tests/               # Unit tests
├── main.py             # Entry point (SeLoger only)
├── scrape.py           # Full scraping script
└── settings.py         # Configuration loader
```

## Configuration Management

The application uses a hierarchical configuration system:

1. **Default values** in configuration modules
2. **Environment variables** override defaults
3. **settings.py** imports all config modules

### Key Environment Variables

- `DISTRICTS`: Comma-separated postal codes to monitor
- `BLACKLISTED_WORDS`: Keywords to exclude from results
- `MIN_PRICE`, `MAX_PRICE`: Price range filters
- `MIN_SIZE`: Minimum surface area
- `MIN_PRICE_PER_SURFACE_UNIT`: Price per square meter threshold
- `DATABASE_URL`: Database connection string
- `LOGGING_LEVEL`: Log verbosity (DEBUG, INFO, WARNING, ERROR)

## Development Notes

### Browser Dependencies

The scrapers use Selenium with PhantomJS (deprecated). For local development:

```bash
# macOS setup
brew install phantomjs
brew cask install chromedriver
```

### Testing

- Uses Python's built-in `unittest` framework
- Test data includes sample JSON/XML responses from real estate sites
- Focus on unit testing for offer model validation and data parsing

### Adding New Scrapers

To add support for a new real estate site:

1. Create new scraper class extending `BaseScraper`
2. Implement required abstract methods:
   - `_get_search_url()`: Return site's search URL
   - `_get_offers()`: Extract offer elements from page
   - `_get_offer_object()`: Return appropriate offer model instance
   - `_is_valid_offer()`: Validate offer before processing
   - `_prepare_offer_filling()`: Prepare data extraction
   - `_has_next_page()`: Check for pagination
3. Add field extraction methods for offer properties
4. Add configuration module in `config/`
5. Register scraper in main execution scripts

### Legacy Notes

- Originally designed for Heroku deployment with Slack integration
- Some deprecated dependencies (PhantomJS, old Python libraries)
- Database integration present but minimal (SQLAlchemy configured)
- Slack notification code has been removed from current codebase