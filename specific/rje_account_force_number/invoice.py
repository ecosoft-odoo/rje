# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    number = fields.Char(states={'draft': [('readonly', False)]})
