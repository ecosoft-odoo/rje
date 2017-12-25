# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    attention = fields.Char(
        string='Attention',
    )
    preprint_number = fields.Char(
        string='Preprint Number',
    )
    day_delivery_term = fields.Char(
        string='Day Delivery Term',
    )
    drawing_number = fields.Char(
        string='Drwaing Number',
        related='order_line.drawing_number',
    )
    amount_discount = fields.Float(
        string='Discount (Amt.)',
        related='order_line.amount_discount',
    )
    percent_discount = fields.Float(
        string='Discount (%)',
        related='order_line.percent_discount',
    )
    approved_employee_id = fields.Many2one(
        'hr.employee',
        string='Approved by',
    )
    header_text = fields.Char(
        string='Header Text',
    )

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    drawing_number = fields.Char(
        string='Drawing Number',
    )
    discount = fields.Float(
        digits=(16,20),
    )
    amount_discount = fields.Float(
        string='Discount (Amt.)',
    )
    percent_discount = fields.Float(
        string='Discount (%)',
    )

    @api.onchange('amount_discount', 'price_unit', 'product_uom_qty')
    def _onchange_amount_discount(self):
        if self._context.get('by_amount_discount', False):
            self.percent_discount = False
            price_subtotal = self.price_unit * self.product_uom_qty
            if not price_subtotal:
                self.discount = 0.0
            else:
                self.discount = self.amount_discount / price_subtotal * 100.0

    @api.onchange('percent_discount')
    def _onchange_discount_percent(self):
        if self._context.get('by_percent_discount', False):
            self.amount_discount = False
            self.discount = self.percent_discount
