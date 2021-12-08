# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


# from vcr import VCR
# from xmlunittest import XmlTestMixin

from odoo.tests.common import SavepointCase


class CommonCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.country = cls.env.ref("base.ch")
        cls.company = cls.env.user.company_id
        cls.company.vat = "CHE-012.345.678"
        cls.company.name = "Camptocamp SA"
        cls.company.street = "StreetOne"
        cls.company.street2 = ""
        cls.company.zip = "1015"
        cls.company.city = "Lausanne"
        cls.company.partner_id.country_id = cls.country
        cls.bank = cls.env.ref("base.res_bank_1")
        cls.bank.clearing = 777
        cls.connection = cls.env["postfinance.service"].create(
            {
                "name": "Test",
                "username": "thierry.ducrest@camptocamp.com",
                "password": "Wv77&UzC8PQR",
                "use_test_service": True,
            }
        )

    def test_connection(self):
        # self.assertTrue(False)
        self.connection.ping_service()
