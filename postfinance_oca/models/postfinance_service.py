# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from postfinanceb2binvoice import PostfinanceSvr

from odoo import fields, models

_logger = logging.getLogger(__name__)


class PostfinanceService(models.Model):
    _name = "postfinance.service"
    _description = "Postfinance service configuration"

    name = fields.Char(required=True)
    username = fields.Char(required=True)
    password = fields.Char(required=True)
    biller_id = fields.Char()
    use_test_service = fields.Boolean(string="Testing", help="Target the test service")
    active = fields.Boolean(default=True)

    def ping_service(self):
        """Ping the service"""
        svr = PostfinanceSvr(self.use_test_service)
        return svr.ping()
