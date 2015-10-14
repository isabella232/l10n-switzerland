# -*- coding: utf-8 -*-
# © 2011-2014 Nicolas Bessi (Camptocamp SA)
# © 2014 Olivier Jossen (brain-tec AG)
# © 2014 Guewen Baconnier (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Switzerland - Postal codes (ZIP) list',
    'version': '9.0.2.0.0',
    'author': '''
        Camptocamp,
        brain-tec AG,
        copadoMEDIA UG,
        Odoo Community Association (OCA)
    ''',
    'category': 'Localisation',
    'website': 'http://www.camptocamp.com',
    'license': 'AGPL-3',
    'summary': 'Provides all Swiss postal codes for auto-completion',
    'depends': [
        'base',
        'base_location',  # in https://github.com/OCA/partner-contact/
        'l10n_ch_states',  # in https://github.com/OCA/l10n-switzerland/
    ],
    'data': ['data/l10n_ch_better_zip.xml'],
    'images': [],
    'demo': [],
    'auto_install': False,
    'installable': True,
    'application': True,
}
