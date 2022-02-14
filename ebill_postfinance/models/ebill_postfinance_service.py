# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import logging.config

from odoo import fields, models
from odoo.exceptions import UserError

from ..einvoicing_postfinance.einvoicing_postfinance import einvoicing_postfinance

_logger = logging.getLogger(__name__)

# Setup debug logging for Zeep
# TODO: logging does not work with Odoo, it disable all other logs
# logging.config.dictConfig({
#     'version': 1,
#     'formatters': {
#         'verbose': {
#             'format': '%(name)s: %(message)s'
#         }
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'verbose',
#         },
#     },
#     'loggers': {
#         'zeep.transports': {
#             'level': 'DEBUG',
#             'propagate': True,
#             'handlers': ['console'],
#         },
#     }
# })


class EbillPostfinanceService(models.Model):
    _name = "ebill.postfinance.service"
    _description = "Postfinance eBill service configuration"

    name = fields.Char(required=True)
    username = fields.Char()
    password = fields.Char()
    biller_id = fields.Char(string="Biller ID", size=17, required=True)
    use_test_service = fields.Boolean(string="Testing", help="Target the test service")
    partner_bank_id = fields.Many2one(
        comodel_name="res.partner.bank", string="Bank account", ondelete="restrict"
    )
    invoice_message_ids = fields.One2many(
        comodel_name="ebill.postfinance.invoice.message",
        inverse_name="service_id",
        string="Invoice Messages",
        readonly=True,
    )
    ebill_payment_contract_ids = fields.One2many(
        comodel_name="ebill.payment.contract",
        inverse_name="postfinance_service_id",
        string="Contracts",
        readonly=True,
    )
    active = fields.Boolean(default=True)
    file_type_to_use = fields.Selection(
        string="Invoice Format",
        default="EAI.XML",
        required=True,
        selection=[
            ("XML", "ybinvoice"),
            ("EAI.XML", "Custom XML (SAPiDoc)"),
            # ("eai.edi", "Custom EDIFACT"),
            ("struct.pdf", "Factur X"),
        ],
    )
    operation_timeout = fields.Integer(
        string="HTTP Timeout",
        default="600",
        help="Timeout for each HTTP (GET, POST) request in seconds.",
    )

    def _get_service(self):
        return einvoicing_postfinance.EbillService(
            self.use_test_service,
            self.username,
            self.password,
            self.biller_id,
            self.operation_timeout,
        )

    def test_ping(self):
        """Test the service from the UI."""
        self.ensure_one()
        msg = ["Test connection to service"]
        res = self.ping_service()
        if res:
            msg.append("Success pinging service \n  Receive :{}".format(res))
        else:
            msg.append(" - Failed pinging service")
        raise UserError("\n".join(msg))

    def ping_service(self, test_error=False, test_exception=False):
        """Ping the service, uses the authentication.

        test_error: will create an unhandled error in the repsonse
        test_exception: will create a FaultException

        """
        service = self._get_service()
        return service.ping()

    def search_invoice(self, transaction_id=None):
        """Get invoice status from the server.

        transaction_id:
        """
        service = self._get_service()
        res = service.search_invoices(transaction_id)
        if res.InvoiceCount == 0:
            _logger.info("Search invoice returned no invoice")
            return res
        if res.InvoiceCount < res.TotalInvoiceCount:
            # TODO handle the case where there is more to download ?
            _logger.info("Search invoice has more to download")
        for message in res.InvoiceList.SearchInvoice:
            record = self.invoice_message_ids.search(
                [("transaction_id", "=", message.TransactionId)]
            )
            if record:
                record.update_message_from_server_data(message)
            else:
                _logger.warning(f"Could not find record for message {message}")
        return res

    def upload_file(self, transaction_id, file_type, data):
        service = self._get_service()
        res = service.upload_files(transaction_id, file_type, data)
        return res

    def get_invoice_list(self, archive_data=False):
        service = self._get_service()
        res = service.get_invoice_list(archive_data)
        return res

    def get_process_protocol_list(self, archive_data=False):
        # Is this the processing result of an invoice ?
        service = self._get_service()
        res = service.get_process_protocol_list(archive_data)
        return res

    def get_ebill_recipient_subscription_status(self, recipient_id):
        service = self._get_service()
        res = service.get_ebill_recipient_subscription_status(recipient_id)
        return res

    def get_registration_protocol_list(self, archive_data=False):
        service = self._get_service()
        res = service.get_registration_protocol_list(archive_data)
        for registration_protocol in res or {}:
            self.get_registration_protocol(registration_protocol.CreateDate)
        return res

    def get_registration_protocol(self, create_date, archive_data=False):
        service = self._get_service()
        res = service.get_registration_protocol(create_date, archive_data)
        return res
