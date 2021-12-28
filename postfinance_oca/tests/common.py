# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from vcr import VCR
from xmlunittest import XmlTestMixin

from odoo.tests.common import SavepointCase


class PostfinanceCommonCase(SavepointCase):
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
                "username": "yb1021209",
                "password": "£cAmp£339955",
                "biller_id": "41101000001021209",
                "use_test_service": True,
            }
        )

        cls.tax7 = cls.env["account.tax"].create(
            {
                "name": "Test tax",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": "7.7",
                "tax_group_id": cls.env.ref("l10n_ch.tax_group_tva_77").id,
            }
        )
        cls.at_receivable = cls.env["account.account.type"].create(
            {
                "name": "Test receivable account",
                "type": "receivable",
                "internal_group": "asset",
            }
        )

        cls.invoice = cls.env["account.move"].create(
            {
                "name": "INV_TEST_01",
                "partner_id": cls.env.ref("base.res_partner_1"),
                "invoice_date_due": "2019-07-01",
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (0, 0, {"name": "A little note", "display_type": "line_note"}),
                    (
                        0,
                        0,
                        {
                            "name": "Phone support",
                            "quantity": 1.0,
                            "price_unit": 4.5,
                            "account_id": cls.at_receivable.id,
                            "tax_ids": [(4, cls.tax7.id, 0)],
                        },
                    ),
                ],
            }
        )
        cls.invoice.action_post()


