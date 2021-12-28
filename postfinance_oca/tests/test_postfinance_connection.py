# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


# from vcr import VCR
# from xmlunittest import XmlTestMixin

from .common import PostfinanceCommonCase

class CommonCase(PostfinanceCommonCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()


    def test_connection(self):
        self.connection.ping_service()

    def test_biller_list(self):
        self.connection.get_biller_list()

    def test_upload_invoice(self):
        self.invoice.prepare_postfinance_report()
        message = invoice.create_paynet_message()
        message.payload = message._generate_payload()
        self.connection.upload_report()

