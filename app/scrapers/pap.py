import settings
from app.scrapers.base_scraper import BaseScraper
from app.models.apartment_offer import ApartmentOffer
from app.models.commerce_offer import CommerceOffer


class Pap(BaseScraper):
    """ Pap datasource. """

    def __init__(self):
        super().__init__()
        self._base_site_url = 'https://www.pap.fr'
        self._base_search_url = 'annonce/location'
        self._page = 1

    def _get_search_url(self):
        print("Building search URL...")
        if settings.filtering.MIN_PRICE > 0 and settings.filtering.MAX_PRICE == 0:
            price_range = "a-partir-de-{}-euros".format(settings.filtering.MIN_PRICE)
        elif settings.filtering.MIN_PRICE == 0 and settings.filtering.MAX_PRICE > 0:
            price_range = "jusqu-a-{}-euros".format(settings.filtering.MAX_PRICE)
        elif settings.filtering.MIN_PRICE > 0 and settings.filtering.MAX_PRICE > 0:
            price_range = "entre-{}-et-{}-euros".format(settings.filtering.MIN_PRICE, settings.filtering.MAX_PRICE)
        else:
            price_range = ''
        if settings.filtering.MIN_SIZE > 0:
            min_size = "a-partir-de-{}-m2".format(settings.filtering.MIN_SIZE)
        else:
            min_size = ''
        search_type = '-'.join(settings.pap.PAP_SEARCH_TYPE)
        site_base = '/'.join([self._base_site_url, self._base_search_url])
        
        # Build URL components, filtering out empty strings to avoid consecutive dashes
        url_parts = [site_base, search_type, settings.pap.PAP_SEARCH_LOCATION, price_range, min_size, str(self._page)]
        url_parts = [part for part in url_parts if part]  # Remove empty strings
        url = '-'.join(url_parts)
        return url

    def _has_next_page(self, root):
        tags = root.find_all(lambda tag: tag.has_attr('class') and tag['class'] == ['next'])
        if len(tags) == 0:
            return False, None
        else:
            self._page += 1
            url = self._get_search_url()
            self.logger.info("Next page {}".format(self._page))
            return True, url

    def _get_offers(self, root):
        return root.find_all(lambda tag: tag.has_attr('class') and 'search-list-item-alt' in tag['class'])

# region fill an offer
    def _get_offer_object(self, r_offer):
        item_title = r_offer.find(lambda tag: tag.has_attr('class') and 'item-title' in tag['class'])
        if item_title and item_title.has_attr('href'):
            url = '/'.join([self._base_site_url, item_title['href']])
            if 'local-commercial' in url or 'local-d-activite' in url:
                return CommerceOffer()
            else:
                return ApartmentOffer()
        return ApartmentOffer()

    def _is_valid_offer(self, offer, r_offer):
        item_title = r_offer.find(lambda tag: tag.has_attr('class') and 'item-title' in tag['class'])
        return item_title and item_title.has_attr('name')

    def _prepare_offer_filling(self, offer, r_offer):
        result = None
        item_title = r_offer.find(lambda tag: tag.has_attr('class') and 'item-title' in tag['class'])
        if item_title and item_title.has_attr('href'):
            href = item_title['href']
            if href.startswith('/'):
                href = href[1:]  # Remove leading slash to avoid double slash
            url = '/'.join([self._base_site_url, href])
            offer.details_url = url
            web_page = self._load_web_page(url)
            if web_page is not None:
                res = web_page.find_all(lambda tag: tag.has_attr('class') and tag['class'] == ['details-item'])
                if res is not None and len(res) > 0:
                    result = res[0]
        return result

    def _clean_offer_filling(self, offer, r_offer, payload):
        pass

    def get_details_url(self, offer, r_offer, payload):
        item_title = r_offer.find(lambda tag: tag.has_attr('class') and 'item-title' in tag['class'])
        if item_title and item_title.has_attr('href'):
            href = item_title['href']
            if href.startswith('/'):
                href = href[1:]  # Remove leading slash to avoid double slash
            url = '/'.join([self._base_site_url, href])
            return url
        return None

    def get_title(self, offer, r_offer, payload):
        title = None
        if payload is not None:
            res = payload.find_all(lambda tag: tag.has_attr('class') and tag['class'] == ['h1'])
            if res is not None and len(res) > 0:
                title = res[0].text.strip()
        return title

    def get_description(self, offer, r_offer, payload):
        desc = None
        if payload is not None:
            res = payload.find_all(lambda tag: tag.has_attr('class') and 'item-description' in  tag['class'])[0].find_all('p')
            if res is not None and len(res) > 0:
                desc = res[0].text
                desc = desc.strip()
        return desc

    def get_id(self, offer, r_offer, payload):
        item_title = r_offer.find(lambda tag: tag.has_attr('class') and 'item-title' in tag['class'])
        if item_title and item_title.has_attr('name'):
            return item_title['name']
        return None

    def get_price(self, offer, r_offer, payload):
        price = None
        item_title = r_offer.find(lambda tag: tag.has_attr('class') and 'item-title' in tag['class'])
        if item_title:
            res = item_title.find_all(lambda tag: tag.has_attr('class') and 'item-price' in tag['class'])
            if res is not None and len(res) > 0:
                price = ''.join(c for c in res[0].text.replace('.','') if c in ['0','1','2','3','4','5','6','7','8','9','0'])
                price = price.strip()
        return price

    def __get_surface_from_field(self, field):
        if field is None:
            return None
        content = field.strip().replace('\t', ' ').replace('\n', ' ')
        surface = None
        high_index = content.find('m²')
        if high_index > -1:
            low_index = content.rfind(' ', 0, high_index)
            if high_index - low_index <= 2:
                low_index = content.rfind(' ', 0, low_index)
            if low_index > -1:
                surface = content[low_index:high_index].strip().replace(',', '.')
                surface = ''.join(c for c in surface if c.isdigit() or c == '.')
        return surface

    def get_surface(self, offer, r_offer, payload):
        surface = self.__get_surface_from_field(offer.title)
        if surface is None:
            surface = self.__get_surface_from_field(offer.description)
        return surface

    def get_created_at(self, offer, r_offer, payload):
        pass

    def get_postal_code(self, offer, r_offer, payload):
        pass

    def get_room_count(self, offer, r_offer, payload):
        pass

    def get_building_year(self, offer, r_offer, payload):
        pass

# endregion
