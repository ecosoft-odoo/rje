# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    preprint_number = fields.Char(
        string='Preprint Number',
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]},
    )
