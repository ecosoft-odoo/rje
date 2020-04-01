# -*- coding: utf-8 -*-
from openerp import models, fields


class account_invoice(models.Model):
    _inherit = "account.invoice"

    internal_number = fields.Char(states={'draft': [('readonly', False)]})
