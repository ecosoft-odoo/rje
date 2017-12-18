# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    _readonly_groups = ['rje_group_read.group_account_invoice_user_readonly']

    @api.multi
    def invoice_validate(self):
        for group in self._readonly_groups:
            if self.env.user.has_group(group):
                raise ValidationError(_('You can not validate!'))
        res = super(AccountInvoice, self).invoice_validae()
        return res
