# -*- coding: utf-8 -*-
from lxml import etree
from openerp import models, fields, api, _


def set_view_readonly(user, groups, view_type, res):
    readonly = True in [user.has_group(x) for x in groups]
    if readonly and view_type in ('tree', 'form'):
        tag = view_type == 'tree' and "/tree" or "/form"  # Invisible CRUD
        doc = etree.XML(res['arch'])
        nodes = doc.xpath(tag)
        for node in nodes:
            node.set('create', 'false')
            node.set('edit', 'false')
            node.set('delete', 'false')
        if view_type == 'form':  # Invisible all buttons
            nodes = doc.xpath('/form/header/button')
            for node in nodes:
                node.set('modifiers', '{"invisible": true}')
        res['arch'] = etree.tostring(doc)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _readonly_groups = ['rje_group_read.group_sale_user_readonly']

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(SaleOrder, self).\
            fields_view_get(view_id=view_id, view_type=view_type,
                            toolbar=toolbar, submenu=submenu)
        # Set View Readonly
        set_view_readonly(self.env.user, self._readonly_groups, view_type, res)
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _readonly_groups = ['rje_group_read.group_purchase_user_readonly']

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(PurchaseOrder, self).\
            fields_view_get(view_id=view_id, view_type=view_type,
                            toolbar=toolbar, submenu=submenu)
        # Set View Readonly
        set_view_readonly(self.env.user, self._readonly_groups, view_type, res)
        return res


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    _readonly_groups = ['rje_group_read.group_account_invoice_user_readonly']

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(AccountInvoice, self).\
            fields_view_get(view_id=view_id, view_type=view_type,
                            toolbar=toolbar, submenu=submenu)
        # Set View Readonly
        set_view_readonly(self.env.user, self._readonly_groups, view_type, res)
        return res


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'
    _readonly_groups = ['rje_group_read.group_account_voucher_user_readonly']

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(AccountVoucher, self).\
            fields_view_get(view_id=view_id, view_type=view_type,
                            toolbar=toolbar, submenu=submenu)
        # Set View Readonly
        set_view_readonly(self.env.user, self._readonly_groups, view_type, res)
        return res

      
class StockMove(models.Model):
    _inherit = 'stock.picking'
    _readonly_groups = ['rje_group_read.group_stock_move_user_readonly']

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(StockMove, self).\
            fields_view_get(view_id=view_id, view_type=view_type,
                            toolbar=toolbar, submenu=submenu)
        # Set View Readonly
        set_view_readonly(self.env.user, self._readonly_groups, view_type, res)
        return res
