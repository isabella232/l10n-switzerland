# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EbillPaymentContract(models.Model):
    _inherit = "ebill.payment.contract"

    paynet_account_number = fields.Char(string="Paynet ID", size=20)
    is_paynet_contract = fields.Boolean(
        compute='_compute_is_paynet_contract', store=False
    )
    paynet_service_id = fields.Many2one(
        comodel_name="paynet.service",
        string="Paynet Service",
        ondelete="restrict",
    )

    @api.depends('transmit_method_id')
    def _compute_is_paynet_contract(self):
        for record in self:
            record.is_paynet_contract = (
                record.transmit_method_id
                == self.env.ref('ebill_paynet.paynet_transmit_method')
            )

    @api.multi
    @api.constrains('transmit_method_id', 'paynet_account_number')
    def _check_paynet_account_number(self):
        for contract in self:
            if not contract.is_paynet_contract:
                continue
            if not contract.paynet_account_number:
                raise ValidationError(
                    _("The Paynet ID is required for a Paynet contract.")
                )

    @api.multi
    @api.constrains('transmit_method_id', 'paynet_service_id')
    def _check_paynet_service_id(self):
        for contract in self:
            if contract.is_paynet_contract and not contract.paynet_service_id:
                raise ValidationError(
                    _("A Paynet service is required for a Paynet contract.")
                )
