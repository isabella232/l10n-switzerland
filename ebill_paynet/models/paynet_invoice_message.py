# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from datetime import datetime

# Needs Jinja 2.10
from jinja2 import Environment, select_autoescape, FileSystemLoader
from odoo import api, fields, models
from odoo.modules.module import get_module_root
from zeep.exceptions import Fault

from ..components.api import PayNetDWS

MODULE_PATH = get_module_root(os.path.dirname(__file__))
INVOICE_TEMPLATE_2013 = 'invoice-2013A.xml'
INVOICE_TEMPLATE_2003 = 'invoice-2003A.xml'
TEMPLATE_DIR = MODULE_PATH + '/messages'

DOCUMENT_TYPE = {'out_invoice': 'EFD', 'out_refund': 'EGS'}

jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(['xml']),
)
template_2013 = jinja_env.get_template(INVOICE_TEMPLATE_2013)
template_2003 = jinja_env.get_template(INVOICE_TEMPLATE_2003)


class PaynetInvoiceMessage(models.Model):
    _name = "paynet.invoice.message"
    _description = "Paynet shipment send to service"

    service_id = fields.Many2one(
        comodel_name="paynet.service",
        string="Paynet Service",
        required=True,
        ondelete="restrict",
        readonly=True,
    )
    invoice_id = fields.Many2one(
        comodel_name="account.invoice", ondelete="restrict"
    )
    attachment_id = fields.Many2one('ir.attachment', 'PDF')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('done', 'Done'),
            ('reject', 'Reject'),
            ('error', 'Error'),
        ],
        default='draft',
    )
    ic_ref = fields.Char(
        string="IC Ref", size=14, help="Document interchange reference"
    )
    # Set with invoice_id.number but also with returned data from server ?
    ref = fields.Char('Reference N°', size=35)
    ebill_account_number = fields.Char('Paynet Id', size=20)
    payload = fields.Text('Payload sent')
    response = fields.Text('Response recieved')
    shipment_id = fields.Char(size=24, help='Shipment Id on Paynet service')

    def _get_ic_ref(self):
        return 'SA%012d' % self.id

    @api.multi
    def send_to_paynet(self):
        for message in self:
            message.payload = message._generate_payload()
            try:
                shipment_id = message.service_id.take_shipment(message.payload)
                message.shipment_id = shipment_id
                message.state = 'sent'
            except Fault as e:
                message.response = PayNetDWS.handle_fault(e)
                message.state = 'error'

    @staticmethod
    def format_date(date_string=None):
        if not date_string:
            date_string = datetime.now()
        return date_string.strftime('%Y%m%d')

    @api.multi
    def _generate_payload(self):
        self.ensure_one()
        assert self.state == 'draft'
        self.ic_ref = self._get_ic_ref()
        if 'isr_reference' in self.invoice_id._fields:
            invoice_esr = self.invoice_id.isr_reference
        else:
            invoice_esr = ''
        # ESR fixed amount, ESP variable amount, NPY no payment
        if self.invoice_id.type == 'out_invoice':
            payment_type = 'ESR'
        else:
            payment_type = 'NPY'
        params = {
            'client_pid': self.service_id.client_pid,
            'invoice': self.invoice_id,
            'invoice_esr': invoice_esr,
            'biller': self.invoice_id.company_id,
            'customer': self.invoice_id.partner_id,
            'pdf_data': self.attachment_id.datas.decode('ascii'),
            'bank': self.invoice_id.partner_bank_id,
            'ic_ref': self.ic_ref,
            'payment_type': payment_type,
            'document_type': DOCUMENT_TYPE[self.invoice_id.type],
            'format_date': self.format_date,
            'ebill_account_number': self.ebill_account_number,
        }
        if self.service_id.service_type == 'b2b':
            payload = template_2003.render(params)
        else:
            payload = template_2013.render(params)
        return payload