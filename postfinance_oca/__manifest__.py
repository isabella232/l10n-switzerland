# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Postfinance B2B Service",
    "summary": "Postfinance B2B Service",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp SA,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-switzerland",
    "depends": [
        "account",
        "l10n_ch_base_bank",
        # "queue_job",
        # "sale",
    ],
    "external_dependencies": {"python": ["postfinanceb2binvoice"]},
    "data": [
        "security/ir.model.access.csv",
    ],
    "demo": [],
}
