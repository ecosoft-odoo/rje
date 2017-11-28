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

    def filter_print_report(self, res, reports):
        action = []
        if res.get('toolbar', False) and \
                res.get('toolbar').get('print', False):
            for act in res.get('toolbar').get('print'):
                if act.get('name') in reports:
                    action.append(act)
            res['toolbar']['print'] = action
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(AccountInvoice, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        # Customer Invoice
        if self._context.get('default_type', False) == 'out_invoice' and\
           self._context.get('type', False) == 'out_invoice' and\
           self._context.get('journal_type', False) == 'sale':
            reports = [
                u'Invoice/Tax Invoice',
            ]
            self.filter_print_report(res, reports)
        # Customer Refund
        elif self._context.get('default_type', False) == 'out_refund' and\
             self._context.get('type', False) == 'out_refund' and\
             self._context.get('journal_type', False) == 'sale_refund':
            reports = [
                u'Customer Refund',
            ]
            self.filter_print_report(res, reports)
        # Suplier Invoice
        elif self._context.get('default_type', False) == 'in_invoice' and\
             self._context.get('type', False) == 'in_invoice' and\
             self._context.get('journal_type', False) == 'purchase':
            reports = []
            self.filter_print_report(res, reports)
        # Suplier Refund
        elif self._context.get('default_type', False) == 'in_refund' and\
             self._context.get('type', False) == 'in_refund' and\
             self._context.get('journal_type', False) == 'purchase_refund':
            reports = []
            self.filter_print_report(res, reports)
        return res

class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    number_cheque = fields.Char(
        string='Cheque No.',
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)],
                'posted': [('readonly', False)]},
    )
    date_cheque = fields.Date(
        string='Cheque Date',
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)],
                'posted': [('readonly', False)]},
    )
    bank_cheque = fields.Char(
        string='Bank',
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)],
                'posted': [('readonly', False)]},
    )
    bank_branch = fields.Char(
        string='Bank Branch',
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)],
                'posted': [('readonly', False)]},
    )
    pay_in_date = fields.Date(
        string='Pay in Date',
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)],
                'posted': [('readonly', False)]},
    )
    bank_account = fields.Char(
        string='Bank Account',
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)],
                'posted': [('readonly', False)]},
    )

    def filter_print_report(self, res, reports):
        action = []
        if res.get('toolbar', False) and \
                res.get('toolbar').get('print', False):
            for act in res.get('toolbar').get('print'):
                if act.get('name') in reports:
                    action.append(act)
            res['toolbar']['print'] = action
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
            toolbar=False,submenu=False):
        res = super(AccountVoucher, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        # Customer Payment
        if self._context.get('type', False) == 'receipt':
            reports = [
                u'Receipt',
                u'Receipt Voucher',
            ]
            self.filter_print_report(res, reports)
        # Suplier Payment
        elif self._context.get('type', False) == 'payment':
            reports = [
                u'Payment Voucher',
            ]
            self.filter_print_report(res, reports)
        return res
