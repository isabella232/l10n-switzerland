# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

from odoo import _, api, fields, models


_logger = logging.getLogger(__name__)


class AccountMove(models.Model):

    _inherit = "account.move"

    def prepare_postfinance_report(self):
        self.ensure_one()
