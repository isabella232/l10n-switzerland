# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from string import Template

from freezegun import freeze_time

from odoo.tools import file_open

from .common import CommonCase


@freeze_time("2019-06-21 09:06:00")
class TestEbillPostfinanceMessage(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_invoice_qr(self):
        """Check XML payload genetated for an invoice."""
        self.invoice.name = "INV_TEST_01"
        self.invoice.invoice_date_due = "2019-07-01"
        message = self.invoice.create_postfinance_ebill()
        message.payload = message._generate_payload()
        # Remove the PDF file data from the XML to ease testing
        lines = message.payload.splitlines()
        for pos, line in enumerate(lines):
            if line.find("Back-Pack") != -1:
                lines.pop(pos)
                break
        payload = "\n".join(lines).encode("utf8")
        # Prepare the XML file that is expected
        expected_tmpl = Template(
            file_open("ebill_postfinance/tests/examples/invoice_qr_b2b.xml").read()
        )
        expected = expected_tmpl.substitute(IC_REF=message.transaction_id).encode(
            "utf8"
        )
        # Remove the comments in the expected xml
        expected_nocomment = [
            line
            for line in expected.split(b"\n")
            if not line.lstrip().startswith(b"<!--")
        ]
        expected_nocomment = b"\n".join(expected_nocomment)
        self.assertFalse(self.compare_xml_line_by_line(payload, expected_nocomment))