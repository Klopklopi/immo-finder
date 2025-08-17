from datetime import datetime


from app.models.base_offer import BaseOffer


class CommerceOffer(BaseOffer):
    """ DAO representing an offer. """

    def __init__(self):
        super().__init__()

    def fill_object(self, datasource, offer, payload):
        super().fill_object(datasource, offer, payload)
